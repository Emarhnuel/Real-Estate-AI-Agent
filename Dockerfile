# Backend Dockerfile - Python FastAPI with uv
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY src/ ./src/

# Create directories for agent data
RUN mkdir -p agent_data/properties agent_data/locations agent_data/decorations decorated_images

# Expose port
EXPOSE 8000

# Run the FastAPI server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
