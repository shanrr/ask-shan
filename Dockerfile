# Dockerfile for Ask-Shan: A self-hosted AI assistant 
# Author: Rakshith Shanbhag


FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY run.sh .

# Make run script executable
RUN chmod +x run.sh

# Expose Streamlit port
EXPOSE 8501

# Expose Ollama port
EXPOSE 11434

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama to start..."\n\
while ! curl -s http://localhost:11434/api/tags > /dev/null; do\n\
    sleep 1\n\
done\n\
echo "Ollama is ready!"\n\
\n\
# Start Streamlit\n\
streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]