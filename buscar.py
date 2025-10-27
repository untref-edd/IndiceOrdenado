#!/usr/bin/env python3
"""
Interfaz CLI para búsquedas con comodines en el índice ordenado.
Soporta búsquedas exactas, prefijos, sufijos y patrones con comodines.
"""

import os
import sys
from typing import Dict, List
import ZODB
import ZODB.FileStorage
from indexar import IndiceOrdenado  # Importar la clase actualizada


class BuscadorCLI:
    """Interfaz de línea de comandos para búsquedas."""
    
    def __init__(self, archivo_db: str = 'index/indice.fs'):
        """
        Inicializa el buscador con la base de datos ZODB.
        
        Args:
            archivo_db: Archivo de base de datos ZODB
        """
        if not os.path.exists(archivo_db):
            print(f"Error: No existe el índice '{archivo_db}'")
            print("Ejecuta 'python indexar.py' o 'make index' primero para crear el índice.")
            sys.exit(1)
        
        # Abrir la base de datos ZODB
        self.storage = ZODB.FileStorage.FileStorage(archivo_db, read_only=True)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()
        
        if not hasattr(self.root, 'indice'):
            print("Error: El índice no está inicializado en la base de datos.")
            sys.exit(1)
        
        self.indice = self.root.indice
        # Forzar que use la clase actualizada
        self.indice.__class__ = IndiceOrdenado
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        try:
            self.connection.close()
        except Exception:
            pass  # Ignorar errores de cierre en read-only
        self.db.close()
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del índice."""
        stats = self.indice.obtener_estadisticas()
        print("\n" + "="*60)
        print("ESTADÍSTICAS DEL ÍNDICE")
        print("="*60)
        print(f"Términos únicos indexados: {stats['total_terminos']}")
        print(f"Documentos en el corpus: {stats['total_documentos']}")
        print(f"\nDocumentos indexados:")
        for doc in sorted(stats['documentos']):
            print(f"  • {doc}")
        print("="*60)
    
    def formatear_resultados(self, resultados: Dict[str, List[str]], 
                            titulo: str = "RESULTADOS"):
        """
        Formatea y muestra los resultados de búsqueda.
        
        Args:
            resultados: Diccionario {término -> lista de documentos}
            titulo: Título a mostrar
        """
        if not resultados:
            print("\n❌ No se encontraron resultados.\n")
            return
        
        print(f"\n{'='*60}")
        print(titulo)
        print('='*60)
        
        # Contar documentos únicos
        docs_unicos = set()
        for docs in resultados.values():
            docs_unicos.update(docs)
        
        print(f"Términos encontrados: {len(resultados)}")
        print(f"Documentos únicos: {len(docs_unicos)}")
        print()
        
        # Mostrar resultados por término
        for termino in sorted(resultados.keys()):
            docs = resultados[termino]
            docs_str = ', '.join(sorted(set(docs)))
            print(f"  📖 '{termino}' → [{docs_str}]")
        
        print('='*60 + '\n')
    
    def buscar_exacto(self, termino: str):
        """Búsqueda exacta de un término."""
        print(f"\n🔍 Buscando término exacto: '{termino}'")
        
        docs = self.indice.buscar_exacto(termino)
        
        if not docs:
            print(f"\n❌ El término '{termino}' no se encuentra en el índice.\n")
        else:
            docs_str = ', '.join(sorted(set(docs)))
            print(f"\n✅ Encontrado en: [{docs_str}]\n")
    
    def buscar_prefijo(self, prefijo: str):
        """Búsqueda por prefijo."""
        print(f"\n🔍 Buscando términos que empiecen con: '{prefijo}'")
        
        resultados = self.indice.buscar_prefijo(prefijo)
        self.formatear_resultados(resultados, 
                                  f"TÉRMINOS QUE EMPIEZAN CON '{prefijo}'")
    
    def buscar_sufijo(self, sufijo: str):
        """Búsqueda por sufijo."""
        print(f"\n🔍 Buscando términos que terminen con: '{sufijo}'")
        
        resultados = self.indice.buscar_sufijo(sufijo)
        self.formatear_resultados(resultados, 
                                  f"TÉRMINOS QUE TERMINAN CON '{sufijo}'")
    
    def buscar_comodin(self, patron: str):
        """Búsqueda con comodines."""
        print(f"\n🔍 Buscando patrón: '{patron}'")
        print("   (usa * para cualquier secuencia, ? para un carácter)")
        
        resultados = self.indice.buscar_comodin(patron)
        self.formatear_resultados(resultados, 
                                  f"TÉRMINOS QUE COINCIDEN CON '{patron}'")
    
    def buscar_comodin_medio(self, patron: str):
        """Búsqueda con comodín en el medio (prefijo*sufijo)."""
        print(f"\n🔍 Buscando patrón con * en el medio: '{patron}'")
        print("   (Usando ambos árboles B+ con intersección AND)")

        resultados = self.indice.buscar_comodin_medio(patron)
        self.formatear_resultados(resultados,
                                  f"TÉRMINOS QUE COINCIDEN CON '{patron}'")
    
    def mostrar_menu(self):
        """Muestra el menú principal."""
        print("\n" + "="*60)
        print("BUSCADOR DE ÍNDICE ORDENADO (Árboles B+ / ZODB)")
        print("="*60)
        print("Opciones de búsqueda:")
        print("  0 - Búsqueda exacta")
        print("  1 - Búsqueda por prefijo (ej: 'hobbi*')")
        print("  2 - Búsqueda por sufijo (ej: '*ción')")
        print("  3 - Búsqueda con comodines (ej: 'h?bbit', 'ho*')")
        print("  4 - Búsqueda con * en medio (ej: 'ca*do', 'ho*bit')")
        print("  5 - Ver estadísticas del índice")
        print("  6 - Salir")
        print("="*60)
    
    def ejecutar(self):
        """Ejecuta el bucle principal del CLI."""
        self.mostrar_estadisticas()

        while True:
            try:
                self.mostrar_menu()
                opcion = input("\nSelecciona una opción (0-6): ").strip()

                if opcion == '6':
                    print("\n👋 ¡Hasta luego!\n")
                    break

                elif opcion == '5':
                    self.mostrar_estadisticas()

                elif opcion == '0':
                    termino = input("\nIngresa el término a buscar: ").strip()
                    if termino:
                        self.buscar_exacto(termino)

                elif opcion == '1':
                    prefijo = input("\nIngresa el prefijo (sin *): ").strip()
                    if prefijo:
                        self.buscar_prefijo(prefijo)

                elif opcion == '2':
                    sufijo = input("\nIngresa el sufijo (sin *): ").strip()
                    if sufijo:
                        self.buscar_sufijo(sufijo)

                elif opcion == '3':
                    prompt = "\nIngresa el patrón "
                    prompt += "(* = cualquier secuencia, ? = un carácter): "
                    patron = input(prompt).strip()
                    if patron:
                        self.buscar_comodin(patron)

                elif opcion == '4':
                    prompt = "\nIngresa el patrón con * en medio "
                    prompt += "(ej: ca*do): "
                    patron = input(prompt).strip()
                    if patron:
                        self.buscar_comodin_medio(patron)

                else:
                    print("\n❌ Opción no válida. Intenta de nuevo.\n")

            except KeyboardInterrupt:
                print("\n\n👋 Búsqueda cancelada. ¡Hasta luego!\n")
                break
            except EOFError:
                print("\n\n👋 ¡Hasta luego!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Función principal."""
    archivo_db = 'index/indice.fs'
    
    buscador = BuscadorCLI(archivo_db)
    
    try:
        buscador.ejecutar()
    finally:
        buscador.cerrar()


if __name__ == '__main__':
    main()
