# Multi-stage build for production
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/.next ./frontend/.next
COPY --from=frontend-builder /app/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/package.json ./frontend/
COPY --from=frontend-builder /app/public ./frontend/public

# Create necessary directories
RUN mkdir -p uploads temp logs

# Expose ports
EXPOSE 8000 3000

# Create startup script
RUN echo '#!/bin/bash\n\
if [ "$1" = "backend" ]; then\n\
  cd /app && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000\n\
elif [ "$1" = "frontend" ]; then\n\
  cd /app/frontend && npm start\n\
elif [ "$1" = "worker" ]; then\n\
  cd /app && python -m celery -A backend.app.tasks.celery_app worker --loglevel=info\n\
elif [ "$1" = "beat" ]; then\n\
  cd /app && python -m celery -A backend.app.tasks.celery_app beat --loglevel=info\n\
elif [ "$1" = "flower" ]; then\n\
  cd /app && python -m celery -A backend.app.tasks.celery_app flower --port=5555\n\
else\n\
  echo "Usage: docker run <image> [backend|frontend|worker|beat|flower]"\n\
  echo "Default: backend"\n\
  cd /app && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000\n\
fi\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default command - can be overridden
CMD ["/app/entrypoint.sh", "backend"]