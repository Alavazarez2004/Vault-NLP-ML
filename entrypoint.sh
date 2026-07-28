#!/bin/sh
set -e

echo "Verificando si ya existen modelos entrenados..."
if [ ! -f "models/kmeans_segmentation.pkl" ]; then
  echo "No se encontraron modelos. Entrenando con datos sinteticos (arranque en frio)..."
  python scripts/train_initial_models.py
else
  echo "Modelos ya existen, se omite el entrenamiento inicial."
fi

echo "Iniciando servidor..."
exec uvicorn main:app --host 0.0.0.0 --port 8006