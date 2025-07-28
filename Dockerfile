FROM python:3.9

WORKDIR /app

# Copy minimal requirements  
COPY requirements-minimal.txt requirements.txt

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN mkdir -p models

ENV PYTHONPATH=/app

CMD ["python", "main.py", "--help"]
