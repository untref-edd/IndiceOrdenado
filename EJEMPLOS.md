# Ejemplos de Uso - Índice Ordenado

Este documento proporciona ejemplos prácticos de uso del índice ordenado.

## Instalación y Setup

```bash
# 1. Clonar o navegar al directorio
cd IndiceOrdenado

# 2. Instalar dependencias
make install
# o: pip install -r requirements.txt

# 3. Crear el índice
make index
# o: python indexar.py
```

## Uso desde Python

### Ejemplo 1: Indexar documentos programáticamente

```python
from indexar import crear_indice

# Indexar el corpus
indice = crear_indice('corpus', 'mi_indice.fs')
```

### Ejemplo 2: Búsquedas desde código

```python
import ZODB
import ZODB.FileStorage
from indexar import IndiceOrdenado

# Abrir el índice
storage = ZODB.FileStorage.FileStorage('indice.fs', read_only=True)
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
indice = root.indice
indice.__class__ = IndiceOrdenado  # Forzar clase actualizada

# Búsqueda exacta
docs = indice.buscar_exacto("hobbit")
print(f"Documentos con 'hobbit': {docs}")
# Output: Documentos con 'hobbit': ['Bombadil', 'Introduccion']

# Ver el posting list (set de doc_ids) para un término
if "hobbit" in indice.indice:
    doc_ids = indice.indice["hobbit"]
    print(f"Posting list para 'hobbit': {doc_ids}")
    # Output: Posting list para 'hobbit': {0, 2}

# Búsqueda por prefijo
resultados = indice.buscar_prefijo("drag")
for termino, docs in resultados.items():
    print(f"{termino}: {docs}")
# Output:
# dragones: ['Bombadil', 'Egidio', 'Introduccion']
# dragón: ['Bombadil', 'Egidio', 'Introduccion']

# Búsqueda con comodines
resultados = indice.buscar_comodin("h*bit")
print(resultados)
# Output: {'hobbit': ['Bombadil', 'Introduccion']}

# Búsqueda con comodín en medio (prefijo*sufijo)
resultados = indice.buscar_comodin_medio("ca*do")
print(f"Encontrados {len(resultados)} términos")
for termino in sorted(resultados.keys())[:5]:
    print(f"  {termino}: {resultados[termino]}")
# Output:
# Encontrados 23 términos
#   cabalgando: ['Niggle', 'Wootton']
#   cachazudo: ['Egidio']
#   caldo: ['Roverandom']
#   calificado: ['Niggle']
#   calmando: ['Roverandom']
# ... (18 términos más)

# Cerrar conexión
connection.close()
db.close()
```

### Ejemplo 3: Estadísticas del índice

```python
import ZODB
import ZODB.FileStorage
from indexar import IndiceOrdenado

storage = ZODB.FileStorage.FileStorage('indice.fs', read_only=True)
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
indice = root.indice
indice.__class__ = IndiceOrdenado

stats = indice.obtener_estadisticas()
print(f"Términos únicos: {stats['total_terminos']}")
print(f"Documentos: {stats['total_documentos']}")
print(f"Lista de documentos: {stats['documentos']}")

connection.close()
db.close()
```

### Ejemplo 4: Iterar sobre términos (Árbol B+ ordenado)

```python
import ZODB
import ZODB.FileStorage
from indexar import IndiceOrdenado

storage = ZODB.FileStorage.FileStorage('indice.fs', read_only=True)
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()
indice = root.indice
indice.__class__ = IndiceOrdenado

# Primeros 20 términos
print("Primeros 20 términos:")
for i, termino in enumerate(indice.indice.keys()):
    if i >= 20:
        break
    print(f"  {termino}")

# Términos en un rango
print("\nTérminos entre 'dragon' y 'elfo':")
for termino in indice.indice.keys(min='dragon', max='elfo'):
    print(f"  {termino}")

connection.close()
db.close()
```

## Uso desde CLI (Interfaz Interactiva)

### Iniciar el buscador

```bash
make search
# o: python buscar.py
```

### Ejemplos de sesión interactiva

```
============================================================
BUSCADOR DE ÍNDICE ORDENADO (Árboles B+ / ZODB)
============================================================
Opciones de búsqueda:
  0 - Búsqueda exacta
  1 - Búsqueda por prefijo
  2 - Búsqueda por sufijo
  3 - Búsqueda con comodines
  4 - Ver estadísticas del índice
  5 - Salir
============================================================

Selecciona una opción (0-5): 0

Ingresa el término a buscar: tolkien

🔍 Buscando término exacto: 'tolkien'

✅ Encontrado en: [Introduccion, Niggle]

---

Selecciona una opción (0-5): 1

Ingresa el prefijo (sin *): hobbi

🔍 Buscando términos que empiecen con: 'hobbi'

============================================================
TÉRMINOS QUE EMPIEZAN CON 'hobbi'
============================================================
Términos encontrados: 2
Documentos únicos: 2

  📖 'hobbit' → [Bombadil, Introduccion]
  📖 'hobbits' → [Bombadil, Introduccion]
============================================================

---

Selecciona una opción (0-5): 3

Ingresa el patrón (* = cualquier secuencia, ? = un carácter): h*bit

🔍 Buscando patrón: 'h*bit'
   (usa * para cualquier secuencia, ? para un carácter)

============================================================
TÉRMINOS QUE COINCIDEN CON 'h*bit'
============================================================
Términos encontrados: 1
Documentos únicos: 2

  📖 'hobbit' → [Bombadil, Introduccion]
============================================================

---

Selecciona una opción (0-6): 4

Ingresa el patrón con * en medio (ej: ca*do): ca*do

🔍 Buscando patrón con * en el medio: 'ca*do'
   (Usando ambos árboles B+ con intersección AND)

============================================================
TÉRMINOS QUE COINCIDEN CON 'ca*do'
============================================================
Términos encontrados: 23
Documentos únicos: 5

  📖 'cabalgando' → [Niggle, Wootton]
  📖 'cachazudo' → [Egidio]
  📖 'caldo' → [Roverandom]
  📖 'calificado' → [Niggle]
  📖 'calmando' → [Roverandom]
  📖 'calzado' → [Bombadil]
  📖 'cambiado' → [Niggle, Roverandom, Wootton]
  ... (16 términos más)
============================================================
```

## Demostración completa

```bash
# Ejecutar script de demostración
make demo
# o: python demo.py

# Ejecutar tests (incluye test de búsqueda con comodín en medio)
make test
# o: python test_indice.py
```

Esto mostrará ejemplos de todas las funcionalidades automáticamente.

## Script end-to-end

```bash
# Crear índice y ejecutar buscador en un comando
make run
# o: python main.py
```

Este script:

1. Verifica si existe el índice
1. Pregunta si quieres reconstruirlo (si existe)
1. Crea/actualiza el índice
1. Lanza el buscador interactivo

## Ejemplos avanzados

### Buscar términos con patrones específicos

```python
# Términos de exactamente 5 letras que empiezan con 'h'
resultados = indice.buscar_comodin("h????")

# Términos que empiezan con 'h' y terminan con 's'
resultados = indice.buscar_comodin("h*s")

# Términos con estructura consonante-vocal-consonante-vocal
resultados = indice.buscar_comodin("?a?o")
```

### Combinar resultados de múltiples búsquedas

```python
# Obtener todos los documentos que contienen términos con 'dragon'
resultados_prefijo = indice.buscar_prefijo("dragon")
resultados_sufijo = indice.buscar_sufijo("dragon")
resultados_medio = indice.buscar_comodin("*dragon*")

# Unir todos los documentos
todos_docs = set()
for resultado in [resultados_prefijo, resultados_sufijo, resultados_medio]:
    for termino, docs in resultado.items():
        todos_docs.update(docs)

print(f"Documentos con variantes de 'dragon': {sorted(todos_docs)}")
```

### Análisis de frecuencias

```python
# Contar cuántos términos empiezan con cada letra
from collections import Counter

contador = Counter()
for termino in indice.indice.keys():
    if termino and termino[0].isalpha():
        contador[termino[0]] += 1

print("Distribución de términos por letra inicial:")
for letra, count in sorted(contador.items()):
    print(f"  {letra}: {count}")
```

## Casos de uso comunes

### 1. Autocompletado

```python
def autocompletar(prefijo, max_resultados=10):
    """Sugiere términos para autocompletar."""
    resultados = indice.buscar_prefijo(prefijo)
    terminos = list(resultados.keys())[:max_resultados]
    return terminos

# Uso
sugerencias = autocompletar("hobbi")
print(f"Sugerencias: {sugerencias}")
# Output: Sugerencias: ['hobbit', 'hobbits']
```

### 2. Corrección ortográfica (fuzzy)

```python
def sugerir_similares(termino, max_distancia=2):
    """Sugiere términos similares usando comodines."""
    sugerencias = []
    
    # Buscar con una letra menos
    patron = termino[:-1] + "*"
    resultados = indice.buscar_comodin(patron)
    sugerencias.extend(resultados.keys())
    
    # Buscar con primera y última letra
    if len(termino) > 2:
        patron = termino[0] + "*" + termino[-1]
        resultados = indice.buscar_comodin(patron)
        sugerencias.extend(resultados.keys())
    
    return list(set(sugerencias))

# Uso
similares = sugerir_similares("hobit")
print(f"¿Quisiste decir?: {similares}")
# Output: ¿Quisiste decir?: ['hobbit', 'hobbits']
```

### 3. Búsqueda de términos raros

```python
# Términos que aparecen en un solo documento
terminos_raros = []
for termino, doc_tree in indice.indice.items():
    if len(doc_tree) == 1:
        terminos_raros.append(termino)

print(f"Términos únicos (en 1 solo doc): {len(terminos_raros)}")
print(f"Ejemplos: {terminos_raros[:10]}")
```

### 4. Exportar términos a CSV

```python
import csv

with open('terminos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Termino', 'Num_Documentos', 'Documentos'])
    
    for termino, doc_tree in indice.indice.items():
        doc_ids = list(doc_tree.keys())
        docs = [indice.documentos[doc_id] for doc_id in doc_ids]
        writer.writerow([termino, len(docs), ', '.join(docs)])

print("Términos exportados a terminos.csv")
```

## Troubleshooting

### Error: "No existe el índice"

```bash
# Crear el índice primero
make index
```

### Error: "AttributeError: ... obtener_estadisticas"

Esto ocurre cuando la clase en ZODB no está actualizada. Solución:

```bash
# Reconstruir el índice
make rebuild
```

### Mejorar rendimiento de búsquedas

```python
# Abrir en modo read-only para búsquedas concurrentes
storage = ZODB.FileStorage.FileStorage('indice.fs', read_only=True)
```

## Próximos pasos

- Explora `ARQUITECTURA.md` para detalles técnicos
- Revisa `test_indice.py` para ver más ejemplos
- Ejecuta `make demo` para ver todas las funcionalidades
- Experimenta con tu propio corpus en `corpus/`
