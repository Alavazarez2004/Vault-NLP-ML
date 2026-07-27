# VAULT AI Service

Microservicio de NLP y Machine Learning para VAULT (plataforma de gestión
de activos personales de valor). Combina en un solo servicio FastAPI:

- **NLP**: sentimiento, toxicidad, entidades (NER + marcas) y tópicos
  sobre posts/comentarios/reseñas de la comunidad.
- **ML**: segmentación de usuarios (K-Means + DBSCAN diagnóstico) y
  recomendaciones basadas en reglas por segmento.

Basado en la arquitectura de [ML_FERMENTADOR](https://github.com/ESTSOFTWARE/ML_FERMENTADOR),
adaptada al dominio de VAULT.

## Requisitos

- Python 3.11+
- Docker
- Dependencias listadas en `requirements.txt`

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

## Configuración

Variables de entorno en `.env` (ver `.env.example`): credenciales de
Supabase, `DATABASE_URL`, y `RABBITMQ_URL` de CloudAMQP. El servicio se
conecta a Postgres **siempre** con `SUPABASE_SERVICE_ROLE_KEY`, nunca con
la anon key.

## Uso

### Entrenar los modelos iniciales (con usuarios sintéticos)

```bash
python -m scripts.train_initial_models
```

### Ejecutar localmente

```bash
uvicorn main:app --reload --port 8006
```

### Usar Docker

```bash
docker compose up --build
```

## Estructura del proyecto

```
├── src/
│   ├── domain/           # Entidades, DTOs, puertos (repositorios abstractos)
│   ├── application/      # Use cases: nlp/, realtime/, training/, dataset_generation/, inference/
│   └── infrastructure/   # FastAPI routes/controllers, adapters (Postgres, RabbitMQ, Joblib), settings
├── data/                 # Datos generados y reales
├── models/               # Modelos entrenados (.pkl)
├── scripts/              # Scripts de utilidad
└── main.py               # Punto de entrada
```

## API

- `POST /api/v1/nlp/analyze` — sentimiento, toxicidad, entidades, tópicos
- `POST /api/v1/ml/segment` — segmenta un usuario en un cluster
- `POST /api/v1/ml/recommend` — recomendaciones para un usuario
- `POST /api/v1/training/retrain` — trigger manual de reentrenamiento incremental
- `GET /api/v1/history/` y `/api/v1/history/user/{user_id}` — historial de segmentación/recomendaciones

### Publisher/Subscriber (RabbitMQ)

Consume `post.created`, `comment.created`, `review.created` (dispara NLP)
y `asset.updated` (recalcula el perfil ML silenciosamente). Publica
`nlp.analyzed` de vuelta para que Community Service (Go) actualice la BD.

## Payloads para testing (local)

```bash
curl -X POST http://localhost:8006/api/v1/nlp/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Excelente restauración, mis Nike quedaron como nuevas",
    "source_id": "11111111-1111-1111-1111-111111111111",
    "source_type": "post"
  }'
```

```bash
curl -X POST http://localhost:8006/api/v1/ml/segment \
  -H "Content-Type: application/json" \
  -d '{"user_id": "11111111-1111-1111-1111-111111111111"}'
```

```bash
curl -X POST http://localhost:8006/api/v1/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "11111111-1111-1111-1111-111111111111"}'
```
