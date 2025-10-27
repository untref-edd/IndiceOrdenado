#!/usr/bin/env python3
"""
Script para visualizar estadísticas del índice de forma gráfica en consola.
"""

import os
import sys
import ZODB
import ZODB.FileStorage
from collections import Counter
from indexar import IndiceOrdenado


def mostrar_estadisticas():
    """Muestra estadísticas detalladas del índice."""

    archivo_db = "index/indice.fs"

    if not os.path.exists(archivo_db):
        print("❌ Error: No existe el índice")
        print("   Ejecuta 'python indexar.py' o 'make index' primero\n")
        sys.exit(1)

    # Abrir el índice
    storage = ZODB.FileStorage.FileStorage(archivo_db, read_only=True)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
    indice = root.indice
    indice.__class__ = IndiceOrdenado

    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS DETALLADAS DEL ÍNDICE")
    print("=" * 70)

    # Estadísticas básicas
    stats = indice.obtener_estadisticas()
    print(f"\n📈 Resumen:")
    print(f"   • Términos únicos: {stats['total_terminos']:,}")
    print(f"   • Documentos: {stats['total_documentos']}")

    # Distribución por letra inicial
    print(f"\n🔤 Distribución por letra inicial:")
    contador_letras = Counter()
    for termino in indice.indice.keys():
        if termino and termino[0].isalpha():
            contador_letras[termino[0]] += 1

    max_count = max(contador_letras.values()) if contador_letras else 1
    for letra in sorted(contador_letras.keys()):
        count = contador_letras[letra]
        barra = "█" * int((count / max_count) * 40)
        print(f"   {letra}: {barra} {count:>4}")

    # Términos más frecuentes (en más documentos)
    print(f"\n📚 Términos que aparecen en más documentos:")
    freq_terminos = []
    for termino, doc_tree in indice.indice.items():
        num_docs = len(doc_tree)
        freq_terminos.append((termino, num_docs))

    freq_terminos.sort(key=lambda x: x[1], reverse=True)
    for termino, num_docs in freq_terminos[:15]:
        print(f"   • '{termino}': {num_docs} documentos")

    # Términos más largos
    print(f"\n📏 Términos más largos:")
    terminos_largos = sorted(indice.indice.keys(), key=len, reverse=True)[:10]
    for i, termino in enumerate(terminos_largos, 1):
        print(f"   {i}. '{termino}' ({len(termino)} caracteres)")

    # Distribución por longitud
    print(f"\n📊 Distribución por longitud de término:")
    contador_longitud = Counter()
    for termino in indice.indice.keys():
        longitud = len(termino)
        if longitud <= 20:  # Agrupar largos
            contador_longitud[longitud] += 1
        else:
            contador_longitud[">20"] += 1

    max_count = max(contador_longitud.values()) if contador_longitud else 1
    for longitud in sorted(contador_longitud.keys(), key=lambda x: x if isinstance(x, int) else 21):
        count = contador_longitud[longitud]
        barra = "█" * int((count / max_count) * 40)
        print(f"   {str(longitud):>3}: {barra} {count:>4}")

    # Documentos con más términos únicos
    print(f"\n📄 Términos únicos por documento:")
    terminos_por_doc = Counter()
    for termino, doc_tree in indice.indice.items():
        for doc_id in doc_tree.keys():
            terminos_por_doc[doc_id] += 1

    for doc_id, count in terminos_por_doc.most_common():
        nombre_doc = indice.documentos[doc_id]
        print(f"   • {nombre_doc}: {count:,} términos únicos")

    # Tamaño del índice
    print(f"\n💾 Tamaño en disco:")
    tamano = os.path.getsize(archivo_db)
    tamano_mb = tamano / (1024 * 1024)
    print(f"   • Archivo: {tamano:,} bytes ({tamano_mb:.2f} MB)")

    # Cerrar conexión
    try:
        connection.close()
    except Exception:
        pass
    db.close()

    print("\n" + "=" * 70)
    print("✅ Análisis completado")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    mostrar_estadisticas()
