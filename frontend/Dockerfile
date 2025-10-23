# frontend/Dockerfile
# Multi-stage: build with Node (Vite) -> serve with nginx (static)
# Assumes your frontend is a Vite app with "npm run build" producing "dist/".
# Adjust NODE_VERSION and NPM commands if using pnpm/yarn.

### STAGE 1: build ###
FROM node:18-alpine AS builder
WORKDIR /app

# Install deps
COPY frontend/package*.json frontend/
COPY frontend/vite.config.* frontend/ 2>/dev/null || true
COPY frontend/.npmrc frontend/ 2>/dev/null || true
RUN npm ci --silent

# Copy source & build
COPY frontend/ /app/
ENV NODE_ENV=production
RUN npm run build

### STAGE 2: runtime (nginx) ###
FROM nginx:1.25-alpine AS runner
# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*
# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: add a small custom nginx conf to enable SPA routing (history API fallback)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["nginx", "-g", "daemon off;"]
