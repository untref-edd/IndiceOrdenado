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
        self.indice = OOBTree()
        self.documentos = OOBTree()
        self.doc_counter = 0
```

- Hereda de `Persistent` para que ZODB la persista
- Cambios a atributos se detectan automáticamente
- Se guarda en la base de datos con `transaction.commit()`

## Estructura de Datos

### Índice

```
IndiceOrdenado (Persistent)
├── indice: OOBTree
│   └── término (str) → OOBTree
│       └── doc_id (int) → True (bool)
├── documentos: OOBTree
│   └── doc_id (int) → nombre_doc (str)
└── doc_counter: int
```

#### Diseño

- **`indice`**: Mapea cada término a un OOBTree de doc_ids
  - Uso de OOBTree anidado permite eficiencia en operaciones de conjuntos
  - Cada doc_id apunta a `True` (simula un set)
  
- **`documentos`**: Mapea doc_ids a nombres de documentos
  - Permite recuperar nombres legibles desde IDs internos
  
- **`doc_counter`**: Contador incremental para asignar IDs únicos

### Ventajas del diseño

1. **Ordenamiento automático**: Los términos se mantienen ordenados sin sort externo
2. **Búsquedas eficientes**: O(log n) para búsqueda exacta
3. **Prefijos rápidos**: `keys(min=prefijo)` aprovecha el orden
4. **Persistencia transparente**: ZODB maneja serialización automáticamente
5. **Sin compresión manual**: ZODB optimiza el almacenamiento internamente

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
            self.indice[termino] = OOBTree()
        self.indice[termino][doc_id] = True
    
    return doc_id
```

**Complejidad**: O(T log N) donde T = términos únicos, N = términos totales en índice

### Búsqueda Exacta

```python
def buscar_exacto(termino: str) -> List[str]:
    termino_norm = self.normalizar_termino(termino)
    if termino_norm not in self.indice:
        return []
    doc_ids = list(self.indice[termino_norm].keys())
    return [self.documentos[doc_id] for doc_id in doc_ids]
```

**Complejidad**: O(log N + D) donde N = términos, D = documentos con el término

### Búsqueda por Prefijo

```python
def buscar_prefijo(prefijo: str) -> Dict[str, List[str]]:
    prefijo_norm = self.normalizar_termino(prefijo)
    resultados = {}
    
    # Iterar desde el prefijo hasta términos que no empiecen con él
    for termino in self.indice.keys(min=prefijo_norm):
        if not termino.startswith(prefijo_norm):
            break
        doc_ids = list(self.indice[termino].keys())
        resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(log N + M) donde M = términos que empiezan con el prefijo

**Ventaja del Árbol B+**: No necesita recorrer todo el índice, aprovecha el orden

### Búsqueda por Sufijo

```python
def buscar_sufijo(sufijo: str) -> Dict[str, List[str]]:
    sufijo_norm = self.normalizar_termino(sufijo)
    resultados = {}
    
    for termino in self.indice.keys():
        if termino.endswith(sufijo_norm):
            doc_ids = list(self.indice[termino].keys())
            resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(N) - debe recorrer todos los términos

**Nota**: Menos eficiente que prefijos, pero inevitable sin índice inverso de sufijos

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
            doc_ids = list(self.indice[termino].keys())
            resultados[termino] = [self.documentos[id] for id in doc_ids]
    
    return resultados
```

**Complejidad**: O(N) - debe verificar cada término contra el patrón

**Optimización posible**: Si el patrón empieza con texto sin comodín, usar prefijo

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
| **Búsquedas** | Booleanas (AND/OR/NOT) | Comodines (*/?) |
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
2. **Sin compresión explícita**: Ocupa más espacio que índice comprimido
3. **Sin búsquedas booleanas**: Solo soporta comodines, no AND/OR/NOT
4. **Términos normalizados**: Pierde información de mayúsculas/acentos

### Mejoras posibles

1. **Índice invertido de sufijos**: Para búsquedas eficientes por sufijo
2. **Trigramas/N-gramas**: Para búsquedas difusas (fuzzy matching)
3. **Operaciones booleanas**: Agregar AND/OR/NOT combinando resultados
4. **Ranking**: TF-IDF o BM25 para ordenar resultados por relevancia
5. **Stemming/Lematización**: Normalización morfológica
6. **Stop words**: Filtrar palabras comunes
7. **Búsquedas fonéticas**: Soundex, Metaphone para similitud de sonido

## Referencias

- [ZODB Documentation](https://zodb.org/)
- [BTrees Package](https://btrees.readthedocs.io/)
- [B+ Tree Wikipedia](https://en.wikipedia.org/wiki/B%2B_tree)
- Apunte de clase: `3-11-indices-arboles-b.md`
