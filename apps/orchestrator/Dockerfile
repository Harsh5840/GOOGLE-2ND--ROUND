FROM python:3.11-slim

WORKDIR /app

# Copy the entire project structure
COPY ../../shared ./shared
COPY ../../agents ./agents
COPY ../../tools ./tools

# Copy orchestrator files
COPY . .

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 