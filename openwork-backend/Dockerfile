# Build stage (optional for Node.js)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Production stage
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production \
    NODE_OPTIONS=--max-old-space-size=512

# Install dumb-init to handle signals properly and curl for healthchecks
RUN apk add --no-cache dumb-init curl

# Copy from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY . .

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]
