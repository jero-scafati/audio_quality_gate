# frontend/Dockerfile
FROM node:22-alpine

WORKDIR /app

# Copiamos package.json e instalamos dependencias
COPY package*.json ./
RUN npm install

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de Vite
EXPOSE 5173

# Comando para desarrollo con host expuesto (necesario para Docker)
CMD ["npm", "run", "dev", "--", "--host"]