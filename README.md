# Índice Ordenado con Árboles B+ (ZODB)

Implementación de un índice ordenado utilizando **Árboles B+** de la biblioteca **ZODB** (Zope Object Database) para Python. Este proyecto permite indexar documentos de texto, persistir el índice en disco, y realizar búsquedas eficientes con soporte para comodines.

> 📚 **[Ver Guía de Inicio Rápido](QUICKSTART.md)** | **[Arquitectura](ARQUITECTURA.md)** | **[Ejemplos](EJEMPLOS.md)**

## 🎯 Características

- **Árboles B+**: Utiliza `OOBTree` de la biblioteca `BTrees` para mantener un índice ordenado
- **Doble índice**: Índice normal + índice con palabras invertidas para búsquedas eficientes por sufijo
- **Persistencia**: Almacenamiento en disco mediante ZODB (no requiere servidor de base de datos)
- **Búsquedas avanzadas**:
  - Búsqueda exacta de términos
  - Búsqueda por prefijo (términos que empiezan con...)
  - Búsqueda por sufijo (términos que terminan con...) usando índice con palabras invertidas
  - Búsqueda con comodines (`*` y `?`)
  - **Búsqueda optimizada prefijo\*sufijo**: Usa ambos árboles B+ con intersección AND
- **Interfaz CLI**: Interfaz de línea de comandos interactiva
- **Normalización**: Conversión a minúsculas y eliminación de puntuación

## 📋 Requisitos

- Python 3.8+
- ZODB >= 5.8.0
- BTrees >= 5.0

## 🚀 Instalación

```bash
# Clonar o navegar al directorio del proyecto
cd IndiceOrdenado

# Instalar dependencias
make install
# o alternativamente:
pip install -r requirements.txt
```

## 📖 Uso

### 1. Indexar el corpus

Primero, indexa los documentos del directorio `corpus/`:

```bash
make index
# o alternativamente:
python indexar.py
```

Este comando:

- Lee todos los archivos `.txt` del directorio `corpus/`
- Crea un índice ordenado usando Árboles B+
- Crea un índice con palabras invertidas (al revés) para búsquedas eficientes por sufijo
- Persiste ambos índices en el archivo `index/indice.fs`

### 2. Ejecutar el buscador

Inicia la interfaz CLI de búsqueda:

```bash
make search
# o alternativamente:
python buscar.py
```

### 3. Opciones de búsqueda

El buscador ofrece las siguientes opciones:

```
0 - Búsqueda exacta
    Busca un término específico
    Ejemplo: "hobbit" → encuentra documentos con "hobbit"

1 - Búsqueda por prefijo
    Encuentra términos que empiezan con el prefijo dado
    Ejemplo: "hobbi" → encuentra "hobbit", "hobbits", etc.

2 - Búsqueda por sufijo
    Encuentra términos que terminan con el sufijo dado
    Ejemplo: "ción" → encuentra "introducción", "canción", etc.

3 - Búsqueda con comodines
    * = cualquier secuencia de caracteres
    ? = exactamente un carácter
    Ejemplos:
      "h*bit" → "hobbit", "habit"
      "el?o" → "elfo" (4 letras)
      "ho*" → "hobbit", "hombre", "hora"

4 - Búsqueda con * en medio (prefijo*sufijo)
    Búsqueda optimizada usando ambos árboles B+
    Usa el índice normal para prefijos e índice con palabras invertidas para sufijos
    Luego hace la intersección (AND) de ambos conjuntos
    Ejemplos:
      "ca*do" → "cansado", "callado", "cambiado", "caminando"
      "ho*bit" → "hobbit"
      "pe*o" → "pero", "peso", "perro", "pequeño"

5 - Ver estadísticas del índice
    Muestra información sobre términos y documentos indexados

6 - Salir
```

## 📁 Estructura del proyecto

```
IndiceOrdenado/
├── README.md              # Documentación principal
├── requirements.txt       # Dependencias Python
├── Makefile              # Automatización de tareas
├── indexar.py            # Creación del índice con Árboles B+
├── buscar.py             # Interfaz CLI de búsqueda
├── test_indice.py        # Tests unitarios
├── corpus/               # Documentos de texto a indexar
│   ├── Bombadil.txt
│   ├── Egidio.txt
│   ├── Introduccion.txt
│   ├── Niggle.txt
│   ├── Roverandom.txt
│   └── Wootton.txt
├── index/                # Base de datos ZODB (generado)
│   └── indice.fs         # Índice persistido
└── tmp/                  # Archivos temporales de tests
```

## 🔧 Comandos Makefile

```bash
make help      # Mostrar ayuda
make install   # Instalar dependencias
make index     # Crear/actualizar el índice
make search    # Ejecutar el buscador interactivo
make stats     # Ver estadísticas del índice
make clean     # Limpiar archivos generados
make rebuild   # Limpiar y reconstruir el índice
make test      # Ejecutar tests
```

## 💡 Ejemplos de uso

### Búsqueda exacta

```
🔍 Buscando término exacto: 'tolkien'
✅ Encontrado en: [Introduccion, Niggle]
```

### Búsqueda por prefijo

```
🔍 Buscando términos que empiecen con: 'hobbi'
TÉRMINOS QUE EMPIEZAN CON 'hobbi'
Términos encontrados: 2
Documentos únicos: 3

  📖 'hobbit' → [Bombadil, Introduccion]
  📖 'hobbits' → [Introduccion]
```

### Búsqueda con comodines

```
🔍 Buscando patrón: 'h*bit'
TÉRMINOS QUE COINCIDEN CON 'h*bit'
Términos encontrados: 1

  📖 'hobbit' → [Bombadil, Introduccion]
```

## 🏗️ Arquitectura

### Árboles B+ (OOBTree)

El índice utiliza `OOBTree` de la biblioteca `BTrees`, que implementa un árbol B+ optimizado:

- **Ordenamiento**: Mantiene las claves (términos) en orden lexicográfico
- **Eficiencia**: Operaciones de búsqueda, inserción y eliminación en O(log n)
- **Rango**: Permite búsquedas eficientes por rango (útil para prefijos)
- **Persistencia**: Integración nativa con ZODB

### Estructura del índice

```python
IndiceOrdenado:
  ├── indice: OOBTree
  │     └── término → set de doc_ids {1, 3, 5}
  ├── indice_invertido: OOBTree
  │     └── término_invertido → set de doc_ids {1, 3, 5}
  ├── documentos: OOBTree
  │     └── doc_id → nombre_documento
  └── doc_counter: int
```

### Búsqueda optimizada con * en medio (prefijo\*sufijo)

La búsqueda con comodín en el medio usa **ambos árboles B+** para máxima eficiencia:

1. **Búsqueda por prefijo** en el índice normal: `indice.keys(min=prefijo)`

   - Aprovecha el orden lexicográfico del árbol B+
   - Complejidad: O(log N + K) donde K = términos con el prefijo

1. **Búsqueda por sufijo** en el índice con palabras invertidas: `indice_invertido.keys(min=sufijo_invertido)`

   - Convierte búsqueda por sufijo en búsqueda por prefijo (palabra invertida)
   - Complejidad: O(log N + M) donde M = términos con el sufijo

1. **Intersección (AND)** de ambos conjuntos

   - Complejidad: O(min(K, M))

**Ejemplo**: `ca*do`

- Índice normal: busca términos que empiezan con "ca" → 316 términos
- Índice con palabras invertidas: busca términos invertidos que empiezan con "od" → 947 términos
- Intersección: 23 términos finales (cansado, callado, cambiado, etc.)
- **Mejora**: ~9.7x más rápido que escanear todos los 12,269 términos

### ZODB (Zope Object Database)

- Base de datos orientada a objetos para Python
- No requiere servidor (almacenamiento en archivo)
- Transacciones ACID
- Objetos Python persistentes de forma transparente

## 🧪 Tests

Ejecutar los tests unitarios:

```bash
make test
# o alternativamente:
python test_indice.py
```

Los tests verifican:

- Operaciones básicas del índice
- Búsquedas exactas, por prefijo, sufijo y comodines
- Persistencia en ZODB
- Indexación del corpus real

## 📚 Referencias

- [ZODB Documentation](https://zodb.org/)
- [BTrees Package](https://btrees.readthedocs.io/)
- Apunte: `3-11-indices-arboles-b.md`
- Proyecto base: [IndiceInvertido](https://github.com/untref-edd/IndiceInvertido)

## 🔍 Diferencias con IndiceInvertido

| Aspecto | IndiceInvertido | IndiceOrdenado |
|---------|-----------------|----------------|
| **Estructura** | Índice invertido (BSBI) | Árboles B+ (OOBTree) |
| **Almacenamiento** | Archivos binarios custom | ZODB |
| **Búsquedas** | Booleanas (AND, OR, NOT) | Comodines (\*, ?) |
| **Compresión** | Front coding + VB | No (ZODB se encarga) |
| **Ordenamiento** | Requiere sort externo | Nativo en B+ |

## 📝 Notas

- El índice se reconstruye completamente en cada ejecución de `indexar.py`
- Los términos se normalizan a minúsculas sin puntuación
- La búsqueda por sufijo recorre todo el índice (menos eficiente)
- Las búsquedas por prefijo aprovechan el orden del árbol B+

## 👤 Autor

Proyecto educativo - UNTREF EDD

## 📄 Licencia

MIT
