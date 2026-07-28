FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# torch CPU-only: el paquete torch normal trae soporte CUDA que no se usa
# en este servicio (corre en CPU) y agrega varios GB innecesarios a la
# imagen. Instalarlo así reduce drásticamente el tamaño final.
RUN pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download es_core_news_sm

COPY . .

RUN mkdir -p data/generated data/real models
RUN chmod +x entrypoint.sh

EXPOSE 8006

CMD ["./entrypoint.sh"]