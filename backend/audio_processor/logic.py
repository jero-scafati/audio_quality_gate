import os
import torch
import torchaudio
from pyannote.audio import Model, Inference
from sklearn.preprocessing import normalize
from sklearn.cluster import AgglomerativeClustering

EMBEDDING_INFERENCE = None

def get_embedding_inference():
    global EMBEDDING_INFERENCE
    if EMBEDDING_INFERENCE is None:
        print("⏳ Cargando modelo Pyannote (esto pasa solo una vez)...")
        token = os.environ.get('HF_TOKEN')
        
        try:
            model = Model.from_pretrained("pyannote/embedding", token=token)
        except TypeError:
            model = Model.from_pretrained("pyannote/embedding", use_auth_token=token)
            
        inference = Inference(model, window="sliding", duration=3.0, step=2.5)
        
        if torch.cuda.is_available():
            inference.to(torch.device("cuda"))
        
        EMBEDDING_INFERENCE = inference
        print("✅ Modelo cargado.")
    
    return EMBEDDING_INFERENCE

def verify_multispeaker(file_path):
    try:
        inference = get_embedding_inference()
        waveform, sample_rate = torchaudio.load(file_path)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        embeddings = inference(file_path)
        
        # 'embeddings' es un SlidingWindowFeature. Lo convertimos a numpy array (n_chunks, dimension)
        X = embeddings.data
        
        if len(X) < 2:
            return False

        # Clustering
        X_normalized = normalize(X, norm='l2', axis=1)
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.6,
            metric='cosine',
            linkage='complete'
        ).fit(X_normalized)
        
        num_clusters = clustering.n_clusters_
        print(f"📊 Clusters detectados: {num_clusters}")
        
        return num_clusters > 1

    except Exception as e:
        print(f"❌ Error procesando audio: {e}")
        return True