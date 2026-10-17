FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download required NLTK resources into the image
RUN python -c "import nltk; [nltk.download(res, quiet=True) for res in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng']]"

# Copy application files
COPY . .

# Ensure upload/output/visualizations directories exist
RUN mkdir -p uploads output visualizations

# Expose default Flask/Gunicorn port
EXPOSE 5000

# Start production server
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120"]
