FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmupdf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libcrypt1 \
    libgcc-s1 \
    libc6 \
    && ln -sf /lib/x86_64-linux-gnu/libcrypt.so.1 /lib/x86_64-linux-gnu/libcrypt.so.2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    PyMuPDF==1.23.0 \
    numpy==1.24.3 \
    scikit-learn==1.3.0

COPY . .

RUN mkdir -p /app/Outputs

ENV PYTHONPATH=/app

CMD ["python", "main.py", "Collection 1"]
