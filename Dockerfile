# Stage 1: Build Frontend
FROM node:18-alpine as frontend_build

WORKDIR /app/frontend

COPY web_dashboard/package*.json ./
RUN npm install

COPY web_dashboard/ ./
RUN npm run build

# Stage 2: Setup Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY utils/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY utils/app ./app

# Copy built frontend assets from Stage 1 to backend static directory
COPY --from=frontend_build /app/frontend/dist ./static

# Expose port
EXPOSE 2026

# Command to run the app
# We run uvicorn on app.main:app
# Since we are in /app, and app code is in /app/app, we need to make sure python path is correct
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2026"]
