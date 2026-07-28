FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download es_core_news_sm

# Descarga los pesos de los modelos de HuggingFace durante el build, para
# que NO se descarguen en cada arranque del contenedor (evita timeouts en
# el primer request y reduce lo que Railway tiene que hacer en runtime).
RUN python -c "from transformers import pipeline; \
    pipeline('text-classification', model='pysentimiento/robertuito-sentiment-analysis'); \
    pipeline('text-classification', model='pysentimiento/robertuito-hate-speech', top_k=None)"

COPY . .

RUN mkdir -p data/generated data/real models
RUN chmod +x entrypoint.sh

EXPOSE 8006

CMD ["./entrypoint.sh"]