# V2 POC Dockerfile - Multi-stage build with uv

# --- Builder Stage ---
# This stage installs the Python dependencies into a virtual environment.
# Using a separate stage keeps the final image smaller.
FROM python:3.13-slim as builder

# Install the uv package manager from its official image.
# This is faster than installing via pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency configuration files.
COPY pyproject.toml uv.lock* README.md ./

# Install dependencies into a virtual environment using uv with cache mount.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


# --- Production Stage ---
# This stage creates the final, lean image for the application.
FROM python:3.13-slim

# Install system dependencies with apt cache mount
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the uv binary from the official image again.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory.
WORKDIR /app

# Copy the dependency configuration files.
COPY pyproject.toml uv.lock* README.md ./

# Copy the pre-built virtual environment from the builder stage.
# This avoids reinstalling all dependencies, making the build much faster.
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code and frontend modules into the container.
COPY app/ app/
COPY frontendclaude/ frontendclaude/
COPY frontendgemini/ frontendgemini/

# Create a non-root user and group for security.
# Running as a non-root user is a critical security best practice.
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --home /home/appuser appuser && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appgroup /app /home/appuser

# Set environment variables for uv cache
ENV UV_CACHE_DIR=/home/appuser/.cache/uv
ENV HOME=/home/appuser

# Switch to the non-root user.
USER appuser

# Expose the port the application will run on.
EXPOSE 8000

# Define a health check to ensure the application is running correctly.
# Docker uses this to determine the container's health status.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Define the command to run the application using the uv runner.
CMD ["uv", "run", "python", "-m", "app.main"]
