FROM quay.io/minio/minio:latest

# Copy helper scripts into image (build context is ./backend)
COPY scripts/entrypoint-minio.sh /entrypoint-minio.sh
COPY scripts/init-minio.sh /init-minio.sh
# Normalize line endings (CRLF -> LF) and ensure scripts are executable.
# Use tr fallback in case sed is not available in base image.
RUN (for f in /entrypoint-minio.sh /init-minio.sh; do \
      if [ -f "$f" ]; then \
        if command -v sed >/dev/null 2>&1; then sed -i 's/\r$//' "$f"; \
        else tr -d '\r' < "$f" > "$f".tmp && mv "$f".tmp "$f"; fi; \
        chmod +x "$f"; \
      fi; \
    done)

# Run the entrypoint with sh to avoid relying on /bin/bash inside the base image.
ENTRYPOINT ["sh", "/entrypoint-minio.sh"]
