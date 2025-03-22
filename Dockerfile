# Global arguments
ARG NODE_VERSION=22
ARG PYTHON3_VERSION=3.12

FROM node:${NODE_VERSION}-slim AS node-builder
WORKDIR /app
COPY package.json package-lock.json tailwind.config.js postcss.config.js .
COPY static ./static
RUN npm install --no-optional \
    && npx @tailwindcss/cli -i ./static/css/global.css -o ./static/css/output.css --minify


############################################
FROM python:${PYTHON3_VERSION}-slim AS python-builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Install MySQL development libraries and build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libpq-dev \
        # Pillow dependencies
        zlib1g-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libopenjp2-7-dev \
    && apt-get clean
COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn


############################################
FROM python:${PYTHON3_VERSION}-slim
LABEL org.opencontainers.image.authors="mat@myframboise.com"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PYTHON3_VERSION

# Environment variables
ENV APP_ENV="production"
# Run migrations/collect static files
ENV RUN_MIGRATIONS="true"
ENV COLLECT_STATIC="true"
# Domain name of the application
ENV DOMAIN="http://localhost"
# Database configuration
ENV DB_ENGINE="sqlite3"
ENV DB_HOST="localhost"
ENV DB_PORT="3306"
ENV DB_DATABASE="database"
ENV DB_USERNAME="root"
ENV DB_PASSWORD="password"
# Admin configuration
ENV ADMIN_USERNAME="admin"
ENV ADMIN_EMAIL=""
ENV ADMIN_PASSWORD="password"

COPY --from=python-builder /usr/local/lib/python${PYTHON3_VERSION}/site-packages/ /usr/local/lib/python${PYTHON3_VERSION}/site-packages/
COPY --from=python-builder /usr/local/bin/ /usr/local/bin/
COPY . .
COPY --from=node-builder /app/static/css/output.css /app/static/css/
RUN chmod +x ./.docker/entrypoint.sh \
    && apt-get update \
    && apt-get install -y \
        curl \
        ca-certificates \
        git \
        gettext \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["/app/.docker/entrypoint.sh"]

HEALTHCHECK --interval=5m --timeout=3s \
    CMD curl -f http://localhost:8000/ || exit 1