FROM quay.io/minio/minio:latest

COPY scripts/entrypoint-minio.sh /entrypoint-minio.sh
COPY scripts/init-minio.sh /init-minio.sh

RUN (for f in /entrypoint-minio.sh /init-minio.sh; do \
      if [ -f "$f" ]; then \
        if command -v sed >/dev/null 2>&1; then sed -i 's/\r$//' "$f"; \
        else tr -d '\r' < "$f" > "$f".tmp && mv "$f".tmp "$f"; fi; \
        chmod +x "$f"; \
      fi; \
    done)

ENTRYPOINT ["sh", "/entrypoint-minio.sh"]