FROM node:18-alpine

# Install OpenSSL for Prisma
RUN apk add --no-cache openssl

WORKDIR /app

COPY package*.json ./
COPY prisma ./prisma
RUN npm install

COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build TypeScript
RUN npm run build

# Create data directory
RUN mkdir -p /data

EXPOSE 3001

# Initialize database and start server
CMD ["sh", "-c", "npx prisma db push --accept-data-loss && npm start"]
