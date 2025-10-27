#!/usr/bin/env python3
"""
Indexación de documentos usando Árboles B+ de ZODB.
Implementa un índice ordenado con persistencia en disco.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
import ZODB
import ZODB.FileStorage
import transaction
from BTrees.OOBTree import OOBTree
from persistent import Persistent


class IndiceOrdenado(Persistent):
    """
    Índice ordenado usando Árboles B+ de ZODB.

    Estructura:
    - indice: OOBTree (término -> set de doc_ids)
    - indice_invertido: OOBTree (término invertido -> set de doc_ids)
    - documentos: OOBTree (doc_id -> nombre del documento)
    """

    def __init__(self):
        super().__init__()
        self.indice = OOBTree()  # término -> set de doc_ids
        # término invertido -> set de doc_ids
        self.indice_invertido = OOBTree()
        self.documentos = OOBTree()  # doc_id -> nombre del documento
        self.doc_counter = 0

    def normalizar_termino(self, termino: str) -> str:
        """Normaliza un término: lowercase y sin puntuación."""
        return re.sub(r"[^\w]", "", termino.lower())

    def agregar_documento(self, nombre_doc: str, contenido: str) -> int:
        """
        Agrega un documento al índice.

        Args:
            nombre_doc: Nombre del documento
            contenido: Contenido del documento

        Returns:
            doc_id: ID asignado al documento
        """
        doc_id = self.doc_counter
        self.doc_counter += 1

        # Registrar el documento
        self.documentos[doc_id] = nombre_doc

        # Tokenizar y agregar términos al índice
        palabras = contenido.split()
        terminos_unicos = set()

        for palabra in palabras:
            termino = self.normalizar_termino(palabra)
            if termino and len(termino) > 0:
                terminos_unicos.add(termino)

        # Agregar términos al índice
        for termino in terminos_unicos:
            if termino not in self.indice:
                self.indice[termino] = set()
            self.indice[termino].add(doc_id)

            # Agregar también al índice con palabras invertidas
            termino_invertido = termino[::-1]  # Invertir la palabra
            if termino_invertido not in self.indice_invertido:
                self.indice_invertido[termino_invertido] = set()
            self.indice_invertido[termino_invertido].add(doc_id)

        return doc_id

    def buscar_exacto(self, termino: str) -> List[str]:
        """
        Busca un término exacto en el índice.

        Args:
            termino: Término a buscar

        Returns:
            Lista de nombres de documentos que contienen el término
        """
        termino_norm = self.normalizar_termino(termino)

        if termino_norm not in self.indice:
            return []

        doc_ids = sorted(self.indice[termino_norm])
        return [self.documentos[doc_id] for doc_id in doc_ids]

    def buscar_prefijo(self, prefijo: str) -> Dict[str, List[str]]:
        """
        Busca todos los términos que empiezan con el prefijo dado.

        Args:
            prefijo: Prefijo a buscar

        Returns:
            Diccionario {término -> lista de documentos}
        """
        prefijo_norm = self.normalizar_termino(prefijo)
        resultados = {}

        # OOBTree mantiene orden lexicográfico
        # Buscar desde el prefijo hasta términos que no empiecen con él
        for termino in self.indice.keys(min=prefijo_norm):
            if not termino.startswith(prefijo_norm):
                break

            doc_ids = sorted(self.indice[termino])
            nombres_docs = [self.documentos[doc_id] for doc_id in doc_ids]
            resultados[termino] = nombres_docs

        return resultados

    def buscar_sufijo(self, sufijo: str) -> Dict[str, List[str]]:
        """
        Busca todos los términos que terminan con el sufijo dado.
        Usa el índice con palabras invertidas para búsqueda eficiente.

        Args:
            sufijo: Sufijo a buscar

        Returns:
            Diccionario {término -> lista de documentos}
        """
        sufijo_norm = self.normalizar_termino(sufijo)
        sufijo_invertido = sufijo_norm[::-1]
        resultados = {}

        # Buscar en el índice con palabras invertidas
        for termino_inv in self.indice_invertido.keys(min=sufijo_invertido):
            if not termino_inv.startswith(sufijo_invertido):
                break

            # Recuperar el término original
            termino = termino_inv[::-1]
            doc_ids = sorted(self.indice_invertido[termino_inv])
            nombres_docs = [self.documentos[doc_id] for doc_id in doc_ids]
            resultados[termino] = nombres_docs

        return resultados

    def buscar_comodin(self, patron: str) -> Dict[str, List[str]]:
        """
        Busca términos que coincidan con un patrón con comodines.

        Soporta:
        - * : cualquier secuencia de caracteres
        - ? : un solo carácter

        Args:
            patron: Patrón con comodines

        Returns:
            Diccionario {término -> lista de documentos}
        """
        # Normalizar patron pero preservar * y ?
        patron_norm = patron.lower()
        # Remover caracteres especiales excepto * y ?
        patron_norm = re.sub(r"[^\w*?]", "", patron_norm)

        # Convertir patrón con comodines a regex
        regex_pattern = patron_norm.replace("*", ".*").replace("?", ".")
        regex_pattern = f"^{regex_pattern}$"

        try:
            regex = re.compile(regex_pattern)
        except re.error:
            return {}

        resultados = {}

        for termino in self.indice.keys():
            if regex.match(termino):
                doc_ids = sorted(self.indice[termino])
                nombres_docs = [self.documentos[doc_id] for doc_id in doc_ids]
                resultados[termino] = nombres_docs

        return resultados

    def buscar_comodin_medio(self, patron: str) -> Dict[str, List[str]]:
        """
        Busca términos con comodín en el medio (prefijo*sufijo).
        Usa ambos árboles B+ para eficiencia: índice para prefijo,
        índice con palabras invertidas para sufijo, luego intersección (AND).

        Ejemplo: ca*do encuentra: cansado, callado, cambiado, etc.

        Args:
            patron: Patrón con * en el medio (ej: "ca*do")

        Returns:
            Diccionario {término -> lista de documentos}
        """
        # Normalizar patron
        patron_norm = patron.lower()
        patron_norm = re.sub(r"[^\w*]", "", patron_norm)

        # Verificar que tenga exactamente un * en el medio
        if patron_norm.count("*") != 1:
            # Si no tiene exactamente un *, usar búsqueda normal
            return self.buscar_comodin(patron)

        # Separar en prefijo y sufijo
        partes = patron_norm.split("*")
        if len(partes) != 2:
            return {}

        prefijo = partes[0]
        sufijo = partes[1]

        # Si prefijo o sufijo vacíos, usar métodos especializados
        if not prefijo:
            return self.buscar_sufijo(sufijo)
        if not sufijo:
            return self.buscar_prefijo(prefijo)

        # 1. Buscar términos con el prefijo en el índice normal
        terminos_con_prefijo = set()
        for termino in self.indice.keys(min=prefijo):
            if not termino.startswith(prefijo):
                break
            terminos_con_prefijo.add(termino)

        # 2. Buscar términos con el sufijo en el índice con palabras invertidas
        sufijo_invertido = sufijo[::-1]
        terminos_con_sufijo = set()
        for termino_inv in self.indice_invertido.keys(min=sufijo_invertido):
            if not termino_inv.startswith(sufijo_invertido):
                break
            termino = termino_inv[::-1]
            terminos_con_sufijo.add(termino)

        # 3. Intersección (AND) de ambos conjuntos de términos
        terminos_coincidentes = terminos_con_prefijo & terminos_con_sufijo

        # 4. Construir resultado con documentos
        resultados = {}
        for termino in sorted(terminos_coincidentes):
            doc_ids = sorted(self.indice[termino])
            nombres_docs = [self.documentos[doc_id] for doc_id in doc_ids]
            resultados[termino] = nombres_docs

        return resultados

    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del índice."""
        return {
            "total_terminos": len(self.indice),
            "total_documentos": len(self.documentos),
            "documentos": list(self.documentos.values()),
        }


def crear_indice(directorio_corpus: str, archivo_db: str = "indice.fs") -> IndiceOrdenado:
    """
    Crea un índice a partir de los documentos en el directorio corpus.

    Args:
        directorio_corpus: Directorio con los archivos .txt
        archivo_db: Archivo de base de datos ZODB

    Returns:
        IndiceOrdenado persistido en disco
    """
    # Abrir/crear la base de datos ZODB
    storage = ZODB.FileStorage.FileStorage(archivo_db)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root()

    # Crear nuevo índice o recuperar existente
    if not hasattr(root, "indice"):
        print("Creando nuevo índice...")
        indice = IndiceOrdenado()
        root.indice = indice
    else:
        print("Recuperando índice existente...")
        indice = root.indice
        # Limpiar índice existente
        indice.indice.clear()
        if hasattr(indice, "indice_invertido"):
            indice.indice_invertido.clear()
        else:
            indice.indice_invertido = OOBTree()
        indice.documentos.clear()
        indice.doc_counter = 0

    # Indexar documentos
    corpus_path = Path(directorio_corpus)
    archivos = sorted(corpus_path.glob("*.txt"))

    print(f"\nIndexando {len(archivos)} documentos...")

    for archivo in archivos:
        nombre_doc = archivo.stem  # Nombre sin extensión
        print(f"  - Indexando: {nombre_doc}")

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            doc_id = indice.agregar_documento(nombre_doc, contenido)

        except Exception as e:
            print(f"    Error al procesar {archivo}: {e}")
            continue

    # Confirmar transacción
    transaction.commit()

    # Mostrar estadísticas
    stats = indice.obtener_estadisticas()
    print(f"\n✓ Índice creado exitosamente:")
    print(f"  - Términos únicos: {stats['total_terminos']}")
    print(f"  - Documentos indexados: {stats['total_documentos']}")
    print(f"  - Archivo de índice: {archivo_db}")

    # Cerrar conexión
    connection.close()
    db.close()

    return indice


def main():
    """Función principal para crear el índice."""
    directorio_corpus = "corpus"
    archivo_db = "index/indice.fs"

    # Crear directorio index si no existe
    os.makedirs("index", exist_ok=True)

    if not os.path.exists(directorio_corpus):
        print(f"Error: No existe el directorio '{directorio_corpus}'")
        sys.exit(1)

    crear_indice(directorio_corpus, archivo_db)


if __name__ == "__main__":
    main()
