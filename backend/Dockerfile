FROM public.ecr.aws/docker/library/python:3.12

WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock gunicorn.conf.py ./
COPY src ./src

# Install dependencies
RUN uv sync --frozen --no-cache

# Port
EXPOSE 8386

# Health Check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD [ "curl", "-f", "http://localhost:8386/healthcheck" ]

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Run the application
CMD ["uv", "run", "gunicorn", "src.main:app", \
  "--config", "gunicorn.conf.py"]
