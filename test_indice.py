#!/usr/bin/env python3
"""
Tests para el índice ordenado con Árboles B+ de ZODB.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import ZODB
import ZODB.FileStorage
import transaction
from indexar import IndiceOrdenado, crear_indice


def test_indice_basico():
    """Test básico de creación y búsqueda en el índice."""
    print("\n" + "="*60)
    print("TEST 1: Operaciones básicas del índice")
    print("="*60)
    
    # Crear directorios necesarios
    os.makedirs('tmp', exist_ok=True)
    
    # Crear índice en memoria
    storage = ZODB.FileStorage.FileStorage('tmp/test_temp.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
    
    indice = IndiceOrdenado()
    root.indice = indice
    
    # Agregar documentos de prueba
    indice.agregar_documento("Doc1", "el hobbit vive en la comarca")
    indice.agregar_documento("Doc2", "el hobbit encontró un anillo")
    indice.agregar_documento("Doc3", "los elfos cantaban canciones")
    
    transaction.commit()
    
    # Test búsqueda exacta
    print("\n✓ Test búsqueda exacta:")
    docs = indice.buscar_exacto("hobbit")
    print(f"  'hobbit' → {docs}")
    assert set(docs) == {"Doc1", "Doc2"}, "Error en búsqueda exacta"
    
    docs = indice.buscar_exacto("elfos")
    print(f"  'elfos' → {docs}")
    assert docs == ["Doc3"], "Error en búsqueda exacta"
    
    # Test búsqueda prefijo
    print("\n✓ Test búsqueda por prefijo:")
    resultados = indice.buscar_prefijo("ho")
    print(f"  'ho*' → {list(resultados.keys())}")
    assert "hobbit" in resultados, "Error en búsqueda por prefijo"
    
    # Test búsqueda sufijo
    print("\n✓ Test búsqueda por sufijo:")
    resultados = indice.buscar_sufijo("bit")
    print(f"  '*bit' → {list(resultados.keys())}")
    assert "hobbit" in resultados, "Error en búsqueda por sufijo"
    
    # Test búsqueda con comodines
    print("\n✓ Test búsqueda con comodines:")
    resultados = indice.buscar_comodin("h*bit")
    print(f"  'h*bit' → {list(resultados.keys())}")
    assert "hobbit" in resultados, "Error en búsqueda con comodines"
    
    resultados = indice.buscar_comodin("el?os")
    print(f"  'el?os' → {list(resultados.keys())}")
    assert "elfos" in resultados, "Error en búsqueda con comodines"
    
    # Limpiar
    connection.close()
    db.close()
    os.remove('tmp/test_temp.fs')
    
    print("\n✅ Todos los tests básicos pasaron correctamente\n")


def test_persistencia():
    """Test de persistencia del índice."""
    print("\n" + "="*60)
    print("TEST 2: Persistencia en ZODB")
    print("="*60)
    
    # Crear directorios necesarios
    os.makedirs('tmp', exist_ok=True)
    
    archivo_db = 'tmp/test_persist.fs'
    
    # Crear índice y agregar datos
    storage = ZODB.FileStorage.FileStorage(archivo_db)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
    
    indice = IndiceOrdenado()
    root.indice = indice
    
    indice.agregar_documento("TestDoc", "test de persistencia en ZODB")
    transaction.commit()
    
    connection.close()
    db.close()
    
    print("✓ Índice guardado en disco")
    
    # Reabrir y verificar
    storage = ZODB.FileStorage.FileStorage(archivo_db, read_only=True)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
    
    indice = root.indice
    docs = indice.buscar_exacto("persistencia")
    
    print(f"✓ Índice recuperado: 'persistencia' → {docs}")
    assert docs == ["TestDoc"], "Error en persistencia"
    
    connection.close()
    db.close()
    
    # Limpiar
    os.remove(archivo_db)
    if os.path.exists(archivo_db + '.index'):
        os.remove(archivo_db + '.index')
    if os.path.exists(archivo_db + '.tmp'):
        os.remove(archivo_db + '.tmp')
    if os.path.exists(archivo_db + '.lock'):
        os.remove(archivo_db + '.lock')
    
    print("✅ Test de persistencia pasó correctamente\n")


def test_corpus_real():
    """Test con el corpus real si existe."""
    print("\n" + "="*60)
    print("TEST 3: Indexación del corpus real")
    print("="*60)
    
    if not os.path.exists('corpus'):
        print("⚠️  Corpus no encontrado, saltando test\n")
        return
    
    # Crear directorios necesarios
    os.makedirs('tmp', exist_ok=True)
    
    archivo_db = 'tmp/test_corpus.fs'
    
    try:
        # Crear índice con el corpus real
        crear_indice('corpus', archivo_db)
        
        # Verificar el índice
        storage = ZODB.FileStorage.FileStorage(archivo_db, read_only=True)
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root()
        
        indice = root.indice
        stats = indice.obtener_estadisticas()
        
        print(f"\n✓ Estadísticas del corpus:")
        print(f"  Términos: {stats['total_terminos']}")
        print(f"  Documentos: {stats['total_documentos']}")
        
        # Búsqueda de ejemplo
        docs = indice.buscar_exacto("tolkien")
        if docs:
            print(f"\n✓ Ejemplo búsqueda 'tolkien': {docs[:3]}...")
        
        connection.close()
        db.close()
        
        print("\n✅ Test con corpus real pasó correctamente\n")
        
    finally:
        # Limpiar
        if os.path.exists(archivo_db):
            os.remove(archivo_db)
        for ext in ['.index', '.tmp', '.lock']:
            if os.path.exists(archivo_db + ext):
                os.remove(archivo_db + ext)


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DEL ÍNDICE ORDENADO")
    print("="*60)
    
    try:
        test_indice_basico()
        test_persistencia()
        test_corpus_real()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
