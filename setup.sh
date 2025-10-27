#!/bin/bash

# Script de configuración inicial para el proyecto IndiceOrdenado

echo "============================================================"
echo "CONFIGURACIÓN INICIAL - ÍNDICE ORDENADO"
echo "Árboles B+ con ZODB"
echo "============================================================"

# Verificar Python
echo ""
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION encontrado"
else
    echo "   ✗ Python 3 no encontrado"
    echo "   Por favor instala Python 3.8 o superior"
    exit 1
fi

# Verificar pip
echo ""
echo "2. Verificando pip..."
if python3 -m pip --version &> /dev/null; then
    echo "   ✓ pip encontrado"
else
    echo "   ✗ pip no encontrado"
    echo "   Por favor instala pip"
    exit 1
fi

# Crear entorno virtual si no existe
echo ""
echo "3. Configurando entorno virtual..."
if [ -d ".venv" ]; then
    echo "   ✓ Entorno virtual ya existe"
else
    echo "   Creando entorno virtual..."
    python3 -m venv .venv
    echo "   ✓ Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "4. Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias
echo ""
echo "5. Instalando dependencias..."
pip install -q -r requirements.txt
echo "   ✓ Dependencias instaladas"

# Verificar corpus
echo ""
echo "6. Verificando corpus..."
if [ -d "corpus" ]; then
    NUM_DOCS=$(ls -1 corpus/*.txt 2>/dev/null | wc -l)
    if [ $NUM_DOCS -gt 0 ]; then
        echo "   ✓ Corpus encontrado: $NUM_DOCS documentos"
    else
        echo "   ⚠️  Carpeta corpus vacía"
        echo "   Agrega archivos .txt en corpus/ para indexar"
    fi
else
    echo "   ✗ Carpeta corpus no encontrada"
    exit 1
fi

# Crear índice
echo ""
echo "7. ¿Deseas crear el índice ahora? (s/N)"
read -r respuesta
if [[ "$respuesta" =~ ^[Ss]$ ]]; then
    echo "   Creando índice..."
    python indexar.py
    echo "   ✓ Índice creado"
else
    echo "   Puedes crear el índice después con: make index"
fi

# Instrucciones finales
echo ""
echo "============================================================"
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "============================================================"
echo ""
echo "Comandos disponibles:"
echo "  make help      - Ver todos los comandos"
echo "  make index     - Crear/actualizar el índice"
echo "  make search    - Ejecutar buscador interactivo"
echo "  make demo      - Ver demostración de funcionalidades"
echo "  make stats     - Ver estadísticas del índice"
echo "  make test      - Ejecutar tests"
echo "  make run       - Proceso completo (indexar + buscar)"
echo ""
echo "Documentación:"
echo "  README.md         - Introducción y uso básico"
echo "  ARQUITECTURA.md   - Detalles técnicos"
echo "  EJEMPLOS.md       - Ejemplos de uso"
echo ""
echo "¡Listo para usar!"
echo "============================================================"
