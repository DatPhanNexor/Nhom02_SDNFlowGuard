# Stage 1: Build React production bundle
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY public/ ./public/
COPY src/ ./src/

ENV REACT_APP_API_BASE_URL=""
RUN npm run build

# Stage 2: Serve via Nginx with reverse proxy
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/healthz > /dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
