<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// --- ESTADOS ---
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const error = ref(null)

// Lista de audios para la tabla
const audioList = ref([])
const currentFilter = ref('all') // 'all', 'accepted', 'rejected'

// --- FUNCIONES ---

const handleFileUpload = (event) => {
  file.value = event.target.files[0]
  result.value = null
  error.value = null
}

const submitAudio = async () => {
  if (!file.value) return
  loading.value = true
  error.value = null
  
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const response = await axios.post('http://localhost:8000/api/analyze/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = response.data
    // Recargar la lista después de subir para ver el nuevo audio
    loadAudios(currentFilter.value)
  } catch (err) {
    console.error(err)
    error.value = "Error al procesar el audio."
  } finally {
    loading.value = false
  }
}

// Función para cargar audios con filtros
const loadAudios = async (filterType) => {
  currentFilter.value = filterType
  let url = 'http://localhost:8000/api/analyze/'
  
  // Aplicar filtros según el botón presionado
  if (filterType === 'accepted') {
    url += '?is_multispeaker=false'
  } else if (filterType === 'rejected') {
    url += '?is_multispeaker=true'
  }
  
  try {
    const response = await axios.get(url)
    audioList.value = response.data
  } catch (err) {
    console.error("Error cargando lista:", err)
  }
}

// Cargar lista inicial al montar el componente
onMounted(() => {
  loadAudios('all')
})
</script>

<template>
  <div class="container">
    <h1>🎧 Audio Quality Gate</h1>
    
    <div class="card upload-section">
      <h3>Subir Nuevo Audio</h3>
      <input type="file" @change="handleFileUpload" accept="audio/*" />
      <button @click="submitAudio" :disabled="!file || loading" class="analyze-btn">
        {{ loading ? 'Analizando...' : 'Analizar Audio' }}
      </button>
      
      <div v-if="result" class="result-box" :class="result.is_multispeaker ? 'rejected-box' : 'approved-box'">
        <strong>Resultado:</strong> {{ result.is_multispeaker ? '⛔ RECHAZADO' : '✅ APROBADO' }}
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <div class="history-section">
      <h3>Historial de Análisis</h3>
      
      <div class="filters">
        <button @click="loadAudios('all')" :class="{ active: currentFilter === 'all' }">Todos</button>
        <button @click="loadAudios('accepted')" :class="{ active: currentFilter === 'accepted' }" class="btn-green">Aceptados</button>
        <button @click="loadAudios('rejected')" :class="{ active: currentFilter === 'rejected' }" class="btn-red">Rechazados</button>
      </div>

      <table class="audio-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Fecha</th>
            <th>Reproductor</th> <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="audio in audioList" :key="audio.id">
            <td>#{{ audio.id }}</td>
            <td>{{ new Date(audio.uploaded_at).toLocaleString() }}</td>
            <td>
              <audio controls :src="audio.file" class="mini-player"></audio>
            </td>
            <td>
              <span v-if="audio.is_multispeaker" class="badge badge-red">Multispeaker</span>
              <span v-else class="badge badge-green">Limpio</span>
            </td>
          </tr>
          <tr v-if="audioList.length === 0">
            <td colspan="4">No hay audios para mostrar en esta categoría.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 900px; /* Agrandé un poquito el ancho para que quepa el player */
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
  text-align: center;
}

.card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analyze-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.analyze-btn:disabled { background-color: #a0c4eb; }

/* Cajas de resultado */
.result-box { margin-top: 1rem; padding: 10px; border-radius: 6px; font-weight: bold; }
.approved-box { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.rejected-box { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Filtros */
.filters { margin-bottom: 1rem; display: flex; justify-content: center; gap: 10px; }
.filters button {
  padding: 8px 16px; border: 1px solid #ccc; background: white; cursor: pointer; border-radius: 20px;
  transition: all 0.2s;
}
.filters button.active { background-color: #333; color: white; border-color: #333; }
.filters button.btn-green.active { background-color: #28a745; border-color: #28a745; }
.filters button.btn-red.active { background-color: #dc3545; border-color: #dc3545; }

/* Tabla */
.audio-table {
  width: 100%; border-collapse: collapse; margin-top: 10px; background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  table-layout: fixed; /* Ayuda a que las columnas no bailen */
}
.audio-table th, .audio-table td { 
  padding: 12px; 
  border-bottom: 1px solid #eee; 
  text-align: left; 
  vertical-align: middle; /* Centra verticalmente el player */
}
.audio-table th { background-color: #f1f3f5; font-weight: 600; }

/* Estilo del reproductor */
.mini-player {
  width: 100%;       /* Ocupa el ancho de la celda */
  height: 40px;      /* Altura estándar */
  max-width: 300px;  /* Que no sea eterno en pantallas grandes */
}

/* Badges */
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
.badge-green { background-color: #d4edda; color: #155724; }
.badge-red { background-color: #f8d7da; color: #721c24; }
</style>