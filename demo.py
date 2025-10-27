#!/usr/bin/env python3
"""
Script de demostración del índice ordenado con Árboles B+.
Muestra ejemplos de uso de todas las funcionalidades.
"""

import os
import sys
import ZODB
import ZODB.FileStorage
from indexar import IndiceOrdenado  # Importar la clase actualizada


def demo_busquedas():
    """Muestra ejemplos de todas las búsquedas disponibles."""

    archivo_db = "index/indice.fs"

    if not os.path.exists(archivo_db):
        print("❌ Error: Primero debes crear el índice con 'python indexar.py' o 'make index'")
        sys.exit(1)

    # Abrir el índice
    storage = ZODB.FileStorage.FileStorage(archivo_db, read_only=True)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()
    indice = root.indice

    # Forzar que use la clase actualizada
    indice.__class__ = IndiceOrdenado

    print("\n" + "=" * 70)
    print("DEMO: ÍNDICE ORDENADO CON ÁRBOLES B+ (ZODB)")
    print("=" * 70)

    # Estadísticas
    stats = indice.obtener_estadisticas()
    print(f"\n📊 Estadísticas del índice:")
    print(f"   • Términos únicos: {stats['total_terminos']}")
    print(f"   • Documentos: {stats['total_documentos']}")
    print(f"   • Corpus: {', '.join(sorted(stats['documentos']))}")

    # Ejemplos de búsquedas
    print("\n" + "=" * 70)
    print("EJEMPLOS DE BÚSQUEDAS")
    print("=" * 70)

    # 1. Búsqueda exacta
    print("\n1️⃣  BÚSQUEDA EXACTA")
    print("-" * 70)

    terminos_ejemplo = ["tolkien", "hobbit", "anillo", "dragon"]
    for termino in terminos_ejemplo:
        docs = indice.buscar_exacto(termino)
        if docs:
            print(f"   '{termino}' → {docs}")
        else:
            print(f"   '{termino}' → (no encontrado)")

    # 2. Búsqueda por prefijo
    print("\n2️⃣  BÚSQUEDA POR PREFIJO")
    print("-" * 70)

    prefijos_ejemplo = ["hobbi", "drag", "elfo"]
    for prefijo in prefijos_ejemplo:
        resultados = indice.buscar_prefijo(prefijo)
        if resultados:
            print(f"   '{prefijo}*' →")
            for termino, docs in sorted(resultados.items())[:3]:  # Máximo 3
                print(f"      • {termino}: {docs[:3]}" + ("..." if len(docs) > 3 else ""))
            if len(resultados) > 3:
                print(f"      ... y {len(resultados) - 3} términos más")
        else:
            print(f"   '{prefijo}*' → (no encontrado)")

    # 3. Búsqueda por sufijo
    print("\n3️⃣  BÚSQUEDA POR SUFIJO")
    print("-" * 70)

    sufijos_ejemplo = ["ción", "dad", "mente"]
    for sufijo in sufijos_ejemplo:
        resultados = indice.buscar_sufijo(sufijo)
        if resultados:
            print(f"   '*{sufijo}' → {len(resultados)} términos encontrados")
            # Mostrar algunos ejemplos
            ejemplos = list(resultados.keys())[:5]
            print(f"      Ejemplos: {', '.join(ejemplos)}")
        else:
            print(f"   '*{sufijo}' → (no encontrado)")

    # 4. Búsqueda con comodines
    print("\n4️⃣  BÚSQUEDA CON COMODINES (* = cualquier secuencia, ? = un carácter)")
    print("-" * 70)

    patrones_ejemplo = ["h*bit", "dr?gon", "elfo?", "ho*"]
    for patron in patrones_ejemplo:
        resultados = indice.buscar_comodin(patron)
        if resultados:
            terminos = list(resultados.keys())[:5]
            print(f"   '{patron}' → {terminos}")
            if len(resultados) > 5:
                print(f"      ... y {len(resultados) - 5} términos más")
        else:
            print(f"   '{patron}' → (no encontrado)")

    # 5. Rango de términos (aprovecha el orden del árbol B+)
    print("\n5️⃣  RANGO DE TÉRMINOS (Árbol B+ ordenado)")
    print("-" * 70)

    print("   Primeros 10 términos alfabéticamente:")
    count = 0
    for termino in indice.indice.keys():
        if count >= 10:
            break
        print(f"      • {termino}")
        count += 1

    print("\n   Términos entre 'hobbit' y 'hombre':")
    count = 0
    for termino in indice.indice.keys(min="hobbit", max="hombre"):
        if count >= 10:
            print("      ...")
            break
        print(f"      • {termino}")
        count += 1

    # Comparación de performance
    print("\n" + "=" * 70)
    print("💡 VENTAJAS DE LOS ÁRBOLES B+")
    print("=" * 70)
    print("   ✓ Mantienen el orden automáticamente")
    print("   ✓ Búsquedas eficientes: O(log n)")
    print("   ✓ Búsquedas por rango muy rápidas (prefijos)")
    print("   ✓ Persistencia transparente con ZODB")
    print("   ✓ No requiere sort externo")

    # Cerrar conexión
    try:
        connection.close()
    except Exception:
        pass  # Ignorar errores de cierre en read-only
    db.close()

    print("\n" + "=" * 70)
    print("🎉 FIN DE LA DEMOSTRACIÓN")
    print("=" * 70)
    print("\n💡 Ejecuta 'python buscar.py' para búsquedas interactivas\n")


if __name__ == "__main__":
    demo_busquedas()
