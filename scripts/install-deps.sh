#!/bin/bash

# Instalar dependencias APT
echo "📦 Instalando dependencias del sistema..."
apt-get update && \
xargs -a ../config/apt-requirements.txt apt-get install -y

# Instalar dependencias Python
echo "🐍 Instalando dependencias Python..."
pip install -r ../config/pip-requirements.txt

echo "✅ Todas las dependencias instaladas correctamente"