#!/usr/bin/env python3
"""
Script principal para ejecutar el proceso completo:
1. Indexar el corpus
2. Ejecutar el buscador interactivo
"""

import sys
import os
from indexar import crear_indice
from buscar import BuscadorCLI


def main():
    """Función principal."""
    print("="*60)
    print("ÍNDICE ORDENADO - Árboles B+ con ZODB")
    print("="*60)
    
    directorio_corpus = 'corpus'
    archivo_db = 'index/indice.fs'
    
    # Crear directorios necesarios
    os.makedirs('index', exist_ok=True)
    os.makedirs('tmp', exist_ok=True)
    
    # Verificar que existe el corpus
    if not os.path.exists(directorio_corpus):
        print(f"\n❌ Error: No existe el directorio '{directorio_corpus}'")
        print("   Crea el directorio 'corpus/' con archivos .txt para indexar.\n")
        sys.exit(1)
    
    # Verificar si ya existe el índice
    if os.path.exists(archivo_db):
        print(f"\n⚠️  Ya existe un índice en '{archivo_db}'")
        respuesta = input("¿Deseas reconstruirlo? (s/N): ").strip().lower()
        
        if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
            print("\n🔨 Reconstruyendo índice...")
            crear_indice(directorio_corpus, archivo_db)
        else:
            print("\n✓ Usando índice existente")
    else:
        print("\n🔨 Creando índice por primera vez...")
        crear_indice(directorio_corpus, archivo_db)
    
    # Ejecutar el buscador
    print("\n" + "="*60)
    print("Iniciando buscador interactivo...")
    print("="*60)
    
    buscador = BuscadorCLI(archivo_db)
    
    try:
        buscador.ejecutar()
    finally:
        buscador.cerrar()


if __name__ == '__main__':
    main()
