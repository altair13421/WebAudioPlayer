FROM archlinux:latest

# 1. Install dependencies
RUN pacman -Syu --noconfirm --needed \
    base-devel \
    python \
    python-pip \
    sqlite \
    && pacman -Scc --noconfirm

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=/app/data/db.sqlite3 \
    SQLITE_DB_PATH=/app/data/db.sqlite3

# 3. Create working directory and data dir
RUN mkdir -p /app/data
WORKDIR /app

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel setuptools --break-system-packages && \
    pip install --no-cache-dir -r requirements.txt --break-system-packages

# 5. Copy project files
COPY . .

# 6. Set proper permissions
RUN chmod 755 /app/data

# 7. Run as non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# 8. Entrypoint script
COPY entrypoint.sh .
ENTRYPOINT ["./entrypoint.sh"]
