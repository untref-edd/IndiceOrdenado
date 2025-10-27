# Arquitectura del Índice Ordenado

## Resumen

Este proyecto implementa un **índice ordenado** usando **Árboles B+** a través de la biblioteca `BTrees` de ZODB, con persistencia completa en disco. A diferencia del proyecto `IndiceInvertido` que usa BSBI y compresión custom, este enfoque aprovecha las estructuras de datos nativas de ZODB para mantener un índice ordenado eficiente.

## Componentes Principales

### 1. Árboles B+ (`OOBTree`)

#### ¿Qué es un Árbol B+?

Un Árbol B+ es una estructura de datos balanceada que:

- **Mantiene datos ordenados**: Las claves se almacenan en orden lexicográfico
- **Operaciones eficientes**: Búsqueda, inserción y eliminación en O(log n)
- **Búsquedas por rango**: Muy eficientes gracias al orden mantenido
- **Nodos internos y hojas**: Los datos están solo en las hojas, optimizando búsquedas

#### `OOBTree` de BTrees

```python
from BTrees.OOBTree import OOBTree
```

- **Object-to-Object BTree**: Clave → Valor (ambos objetos Python)
- **Ordenamiento lexicográfico**: Las claves se mantienen ordenadas automáticamente
- **Persistencia con ZODB**: Integración nativa, cambios se persisten automáticamente
- **Métodos útiles**:
  - `keys(min=x, max=y)`: Iterar sobre rango de claves
  - `items()`, `values()`: Acceso a datos
  - `__contains__`, `__getitem__`: Interfaz de diccionario

### 2. ZODB (Zope Object Database)

#### Características

- **Base de datos orientada a objetos**: Persiste objetos Python directamente
- **Sin servidor**: Almacenamiento en archivo (FileStorage)
- **Transacciones ACID**: Garantías de consistencia
- **Transparente**: Los objetos se comportan igual en memoria que persistidos

#### Uso en el proyecto

```python
import ZODB
import ZODB.FileStorage
import transaction

# Crear/abrir base de datos
storage = ZODB.FileStorage.FileStorage('indice.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root()

# Usar objetos persistentes
root.indice = IndiceOrdenado()
transaction.commit()  # Guardar cambios

# Cerrar
connection.close()
db.close()
```

### 3. Clase `Persistent`

```python
from persistent import Persistent

class IndiceOrdenado(Persistent):
    def __init__(self):
        super().__init__()
        self.indice = OOBTree()  # término -> set de doc_ids
        self.indice_invertido = OOBTree()  # término invertido -> set de doc_ids
        self.documentos = OOBTree()
        self.doc_counter = 0
```

- Hereda de `Persistent` para que ZODB la persista
- Mantiene **dos árboles B+**: uno normal y uno con palabras invertidas
- Cada término mapea a un **set de Python** con los doc_ids (postings)
- Cambios a atributos se detectan automáticamente
- Se guarda en la base de datos con `transaction.commit()`

## Estructura de Datos

### Índice

```
IndiceOrdenado (Persistent)
├── indice: OOBTree
│   └── término (str) → set de doc_ids {1, 3, 5}
├── indice_invertido: OOBTree
│   └── término_invertido (str) → set de doc_ids {1, 3, 5}
├── documentos: OOBTree
│   └── doc_id (int) → nombre_doc (str)
└── doc_counter: int
```

#### Diseño

- **`indice`**: Mapea cada término a un set de doc_ids

  - Uso de set nativo de Python para operaciones eficientes
  - Garantiza unicidad de doc_ids por término
  - Ejemplo: `indice["hobbit"] = {1, 3, 5}`

- **`indice_invertido`**: Mapea cada término **invertido** a un set de doc_ids

  - Permite búsquedas eficientes por sufijo (convertidas a búsquedas por prefijo)
  - Mismo esquema que el índice normal pero con palabras al revés
  - Ejemplo: `indice_invertido["tibboh"] = {1, 3, 5}`

- **`documentos`**: Mapea doc_ids a nombres de documentos

  - Permite recuperar nombres legibles desde IDs internos

- **`doc_counter`**: Contador incremental para asignar IDs únicos

### Ventajas del diseño

1. **Ordenamiento automático**: Los términos se mantienen ordenados sin sort externo
1. **Búsquedas eficientes**: O(log n) para búsqueda exacta
1. **Prefijos rápidos**: `keys(min=prefijo)` aprovecha el orden
1. **Sufijos rápidos**: Índice con palabras invertidas convierte sufijos en prefijos
1. **Búsqueda prefijo\*sufijo optimizada**: Intersección de sets sobre búsquedas en ambos árboles
1. **Sets nativos**: Operaciones de conjunto eficientes (add, union, intersection)
1. **Postings simples**: `indice["palabra"] = {doc_id1, doc_id2}` - estructura clara
1. **Persistencia transparente**: ZODB maneja serialización automáticamente
1. **Sin compresión manual**: ZODB optimiza el almacenamiento internamente

## Operaciones

### Indexación

```python
def agregar_documento(nombre_doc: str, contenido: str) -> int:
    doc_id = self.doc_counter
    self.doc_counter += 1
    self.documentos[doc_id] = nombre_doc
    
    # Tokenizar y normalizar
    palabras = contenido.split()
    terminos_unicos = set()
    for palabra in palabras:
        termino = self.normalizar_termino(palabra)
        if termino:
            terminos_unicos.add(termino)
    
    # Agregar al índice
    for termino in terminos_unicos:
        if termino not in self.indice:
            self.indice[termino] = set()
        self.indice[termino].add(doc_id)
        
        # Agregar también al índice con palabras invertidas
        termino_invertido = termino[::-1]
        if termino_invertido not in self.indice_invertido:
            self.indice_invertido[termino_invertido] = set()
        self.indice_invertido[termino_invertido].add(doc_id)
    
    return doc_id
```

**Complejidad**: O(T log N) donde T = términos únicos, N = términos totales en índice

### Búsqueda Exacta

```python
def buscar_exacto(termino: str) -> List[str]:
    termino_norm = self.normalizar_termino(termino)
    if termino_norm not in self.indice:
        return []
    doc_ids = sorted(self.indice[termino_norm])
    return [self.documentos[doc_id] for doc_id in doc_ids]
```

**Complejidad**: O(log N + D log D) donde N = términos, D = documentos con el término

- O(log N): buscar término en el árbol B+
- O(D log D): ordenar los doc_ids del set

### Búsqueda por Prefijo

```python
def buscar_prefijo(prefijo: str) -> Dict[str, List[str]]:
    prefijo_norm = self.normalizar_termino(prefijo)
    resultados = {}
    
    # Iterar desde el prefijo hasta términos que no empiecen con él
    for termino in self.indice.keys(min=prefijo_norm):
        if not termino.startswith(prefijo_norm):
            break
        doc_ids = sorted(self.indice[termino])
        resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(log N + M * D log D) donde M = términos con prefijo, D = docs promedio por término

**Ventaja del Árbol B+**: No necesita recorrer todo el índice, aprovecha el orden

### Búsqueda por Sufijo

```python
def buscar_sufijo(sufijo: str) -> Dict[str, List[str]]:
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
        resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(log N + M * D log D) donde M = términos con sufijo, D = docs promedio por término

**Ventaja del índice con palabras invertidas**: Convierte búsqueda por sufijo en búsqueda por prefijo

### Búsqueda con Comodines

```python
def buscar_comodin(patron: str) -> Dict[str, List[str]]:
    # Normalizar patron preservando * y ?
    patron_norm = patron.lower()
    patron_norm = re.sub(r'[^\w*?]', '', patron_norm)
    
    # Convertir a regex
    regex_pattern = patron_norm.replace('*', '.*').replace('?', '.')
    regex_pattern = f'^{regex_pattern}$'
    regex = re.compile(regex_pattern)
    
    resultados = {}
    for termino in self.indice.keys():
        if regex.match(termino):
            doc_ids = sorted(self.indice[termino])
            resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(N * R + M * D log D)

- N = todos los términos del índice
- R = costo de evaluar regex
- M = términos que coinciden
- D = docs promedio por término

**Optimización posible**: Si el patrón empieza con texto sin comodín, usar prefijo

### Búsqueda con Comodín en Medio (prefijo\*sufijo)

```python
def buscar_comodin_medio(patron: str) -> Dict[str, List[str]]:
    # Normalizar y separar en prefijo y sufijo
    patron_norm = patron.lower()
    partes = patron_norm.split('*')
    prefijo = partes[0]
    sufijo = partes[1]
    
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
        resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(log N + K + log N + M + I + I * D log D)

- K = términos con el prefijo
- M = términos con el sufijo
- I = tamaño de la intersección (términos coincidentes)
- D = docs promedio por término
- Intersección de sets: O(min(K, M)) ≈ O(I)

**Ventaja clave**: No usa filtros regex, solo operaciones de conjunto sobre búsquedas eficientes en B+

**Ejemplo**: `ca*do`

- Búsqueda por prefijo "ca": 316 términos
- Búsqueda por sufijo "do": 947 términos
- Intersección: 23 términos (cansado, callado, cambiado, etc.)
- vs Escaneo completo: 12,269 términos
- **Mejora: ~9.7x más rápido**

## Persistencia

### Archivo ZODB

```
index/
  ├── indice.fs         # Archivo principal de datos
  ├── indice.fs.index   # Índice de posiciones (generado automáticamente)
  ├── indice.fs.tmp     # Archivos temporales durante escritura
  └── indice.fs.lock    # Lock para prevenir accesos concurrentes

tmp/                    # Archivos temporales de tests
```

### Transacciones

```python
# Modificar datos
indice.agregar_documento("Doc1", "contenido")

# Confirmar cambios (escribir a disco)
transaction.commit()

# O descartar cambios
transaction.abort()
```

### Modo Read-Only

```python
storage = ZODB.FileStorage.FileStorage('indice.fs', read_only=True)
```

- Evita locks
- Útil para búsquedas concurrentes
- No puede hacer `commit()`

## Comparación con IndiceInvertido

| Aspecto | IndiceInvertido (BSBI) | IndiceOrdenado (B+) |
|---------|------------------------|---------------------|
| **Estructura** | Índice invertido custom | Árbol B+ (OOBTree) |
| **Ordenamiento** | Sort externo en bloques | Automático en B+ |
| **Persistencia** | Archivos binarios custom | ZODB |
| **Compresión** | Front coding + VB | ZODB interno |
| **Búsquedas** | Booleanas (AND/OR/NOT) | Comodines (\*/?) |
| **Prefijos** | Requiere escaneo | Eficiente con B+ |
| **Complejidad** | O(n log n) construcción | O(n log n) inserción |
| **Ventajas** | Compresión explícita | Simplicidad, orden |

## Rendimiento

### Indexación (6 documentos, ~12,000 términos)

```
Tiempo: ~2-3 segundos
Memoria: ~50 MB
Disco: ~2.5 MB (indice.fs)
```

### Búsquedas

- **Exacta**: < 1 ms
- **Prefijo**: < 5 ms (para prefijos comunes)
- **Sufijo**: 50-100 ms (escaneo completo)
- **Comodines**: 50-100 ms (escaneo + regex)

## Limitaciones y Mejoras

### Limitaciones actuales

1. **Búsqueda por sufijo lenta**: Requiere recorrer todo el índice
1. **Sin compresión explícita**: Ocupa más espacio que índice comprimido
1. **Sin búsquedas booleanas**: Solo soporta comodines, no AND/OR/NOT
1. **Términos normalizados**: Pierde información de mayúsculas/acentos

### Mejoras posibles

1. **Índice invertido de sufijos**: Para búsquedas eficientes por sufijo
1. **Trigramas/N-gramas**: Para búsquedas difusas (fuzzy matching)
1. **Operaciones booleanas**: Agregar AND/OR/NOT combinando resultados
1. **Ranking**: TF-IDF o BM25 para ordenar resultados por relevancia
1. **Stemming/Lematización**: Normalización morfológica
1. **Stop words**: Filtrar palabras comunes
1. **Búsquedas fonéticas**: Soundex, Metaphone para similitud de sonido

## Referencias

- [ZODB Documentation](https://zodb.org/)
- [BTrees Package](https://btrees.readthedocs.io/)
- [B+ Tree Wikipedia](https://en.wikipedia.org/wiki/B%2B_tree)
- Apunte de clase: `3-11-indices-arboles-b.md`
