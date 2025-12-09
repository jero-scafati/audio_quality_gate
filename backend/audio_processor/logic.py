import os
import torch
import torchaudio
import numpy as np
from pyannote.audio import Model, Inference
from sklearn.preprocessing import normalize
from sklearn.cluster import AgglomerativeClustering

# --- BLOQUE DE SEGURIDAD PYTORCH (Mantener por compatibilidad) ---
try:
    from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
except ImportError:
    try:
        from pytorch_lightning.callbacks.early_stopping import EarlyStopping
        from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
    except ImportError:
        EarlyStopping = None
        ModelCheckpoint = None

try:
    from omegaconf.listconfig import ListConfig
    from omegaconf.dictconfig import DictConfig
except ImportError:
    ListConfig = None
    DictConfig = None
# -----------------------------------------------------------------

EMBEDDING_INFERENCE = None

def get_embedding_inference():
    global EMBEDDING_INFERENCE
    if EMBEDDING_INFERENCE is None:
        print("⏳ Cargando modelo Pyannote...")
        
        # Aplicar parches de seguridad si es necesario
        allowed_globals = []
        if EarlyStopping is not None: allowed_globals.append(EarlyStopping)
        if ModelCheckpoint is not None: allowed_globals.append(ModelCheckpoint)
        if ListConfig is not None: allowed_globals.append(ListConfig)
        if DictConfig is not None: allowed_globals.append(DictConfig)
            
        if allowed_globals:
            try:
                torch.serialization.add_safe_globals(allowed_globals)
            except AttributeError:
                pass 
            
        token = os.environ.get('HF_TOKEN')
        
        try:
            model = Model.from_pretrained("pyannote/embedding", token=token)
        except TypeError:
            model = Model.from_pretrained("pyannote/embedding", use_auth_token=token)
            
        # CAMBIO CLAVE: Usamos 'whole' para que calcule el embedding del chunk completo
        # que nosotros le pasemos manualmente (tus 5 segundos).
        inference = Inference(model, window="whole")
        
        if torch.cuda.is_available():
            inference.to(torch.device("cuda"))
        
        EMBEDDING_INFERENCE = inference
        print("✅ Modelo cargado (Modo: Whole Window).")
    
    return EMBEDDING_INFERENCE

def extract_fixed_chunks(
    waveform: torch.Tensor,
    sample_rate: int,
    chunk_duration_s: float = 4.0, 
    step_duration_s: float = 2.0,
    min_chunk_duration_s: float = 2.0
):
    num_frames = waveform.shape[1]
    chunk_size_frames = int(chunk_duration_s * sample_rate)
    step_size_frames = int(step_duration_s * sample_rate)
    min_chunk_frames = int(min_chunk_duration_s * sample_rate)

    start = 0
    while start + min_chunk_frames <= num_frames:
        end = start + chunk_size_frames
        chunk = waveform[:, start:end]
        yield chunk # Retornamos el tensor tal cual [canales, frames]
        start += step_size_frames

def verify_multispeaker(file_path):
    try:
        inference = get_embedding_inference()
        waveform, sample_rate = torchaudio.load(file_path)

        # 1. Re-muestreo a 16kHz (Igual que en tu tesis)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
            sample_rate = 16000 # Actualizamos variable

        # 2. Convertir a Mono
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        # 3. Extracción manual de chunks (Tu lógica original)
        # Usamos tus valores por defecto: 5s de duración, 2.5s de paso
        speech_chunks = list(extract_fixed_chunks(waveform, sample_rate, chunk_duration_s=5.0, step_duration_s=2.5))
        
        if len(speech_chunks) < 2:
            print("⚠️ Audio muy corto para analizar (menos de 2 chunks).")
            return False

        # 4. Obtener embeddings para cada chunk
        all_embeddings = []
        for chunk in speech_chunks:
            # Pyannote espera [channels, time]. Nuestros chunks ya vienen así.
            # Pasamos waveform=chunk directamente.
            embedding = inference({"waveform": chunk, "sample_rate": sample_rate})
            all_embeddings.append(embedding)

        if not all_embeddings:
            return False

        # 5. Clustering
        embeddings_np = np.vstack(all_embeddings)
        
        if embeddings_np.shape[0] < 2:
            return False
            
        X_normalized = normalize(embeddings_np, norm='l2', axis=1)
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.6,
            metric='cosine',
            linkage='complete'
        ).fit(X_normalized)
        
        num_clusters = clustering.n_clusters_
        print(f"📊 Clusters detectados (Manual Chunks): {num_clusters}")
        
        return num_clusters > 1

    except Exception as e:
        import traceback
        print(f"❌ Error procesando audio: {e}")
        traceback.print_exc()
        return True