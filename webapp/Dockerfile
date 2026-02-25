FROM node:20-alpine

WORKDIR /app

# Installer les dépendances
COPY package.json ./
RUN npm install


COPY . .


EXPOSE 5173

# Lancer le serveur de dev Vite
CMD ["npm", "run", "dev", "--", "--host"]
