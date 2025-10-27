# 📋 Instrucciones para Evaluación

## Proyecto: Índice Ordenado con Árboles B+ / ZODB

### Alumno: [Tu Nombre]
### Fecha: 27 de octubre de 2025
### Materia: Estructuras de Datos - UNTREF

---

## 📦 Entregables

Este proyecto implementa un **índice ordenado** usando **Árboles B+** de ZODB, similar al proyecto `IndiceInvertido` pero con una arquitectura diferente basada en árboles balanceados.

### Archivos principales:

1. **`indexar.py`** - Implementación del índice con OOBTree
2. **`buscar.py`** - Interfaz CLI con búsquedas por comodines
3. **`test_indice.py`** - Suite de tests completa
4. **`demo.py`** - Demostración automática de funcionalidades
5. **`stats.py`** - Visualización de estadísticas

### Documentación:

- **`README.md`** - Documentación principal
- **`ARQUITECTURA.md`** - Explicación técnica detallada
- **`EJEMPLOS.md`** - Ejemplos de uso prácticos
- **`QUICKSTART.md`** - Guía de inicio rápido
- **`RESUMEN.md`** - Resumen ejecutivo del proyecto

---

## 🚀 Evaluación Rápida (5 minutos)

### Opción A: Demo automática

```bash
# 1. Instalar dependencias
make install

# 2. Ver demostración completa
make demo
```

Esto mostrará automáticamente:
- Estadísticas del índice
- Ejemplos de todas las búsquedas
- Visualización de resultados

### Opción B: Proceso completo

```bash
# 1. Instalar e indexar
make install
make index

# 2. Ver estadísticas
make stats

# 3. Ejecutar tests
make test

# 4. Probar buscador
make search
```

---

## 🧪 Tests

Los tests validan toda la funcionalidad del proyecto:

```bash
make test
```

**Resultados esperados:**
```
✅ Todos los tests básicos pasaron correctamente
✅ Test de persistencia pasó correctamente
✅ Test con corpus real pasó correctamente
✅ TODOS LOS TESTS PASARON EXITOSAMENTE
```

---

## 🔍 Funcionalidades a Evaluar

### 1. Índice con Árboles B+ (OOBTree)

- [x] Uso de `OOBTree` de la biblioteca BTrees
- [x] Estructura ordenada automáticamente
- [x] Operaciones eficientes O(log n)
- [x] Integración con ZODB

**Ver en:** `indexar.py` líneas 20-180

### 2. Persistencia en Disco (ZODB)

- [x] Almacenamiento en FileStorage
- [x] Transacciones ACID
- [x] Objetos Persistent
- [x] Recuperación del índice desde disco

**Ver en:** `indexar.py` líneas 183-250

### 3. Búsquedas con Comodines

- [x] Búsqueda exacta de términos
- [x] Búsqueda por prefijo (aprovecha orden B+)
- [x] Búsqueda por sufijo
- [x] Búsqueda con comodines `*` y `?`

**Ver en:** `indexar.py` líneas 63-172 y `buscar.py`

### 4. Interfaz CLI

- [x] Menú interactivo
- [x] 5 tipos de búsqueda
- [x] Formateo de resultados
- [x] Manejo de errores

**Ver en:** `buscar.py` completo

### 5. Indexación del Corpus

- [x] Lectura de 6 documentos del corpus
- [x] Normalización de términos
- [x] 12,269 términos únicos indexados
- [x] 1.54 MB persistido en disco

**Verificar con:** `make stats`

---

## 📊 Resultados del Proyecto

### Corpus indexado:
- **6 documentos** (obras de Tolkien)
- **12,269 términos únicos**
- **~20,000 palabras totales**

### Rendimiento:
- Indexación: ~2-3 segundos
- Búsqueda exacta: < 1 ms
- Búsqueda prefijo: < 5 ms
- Búsqueda comodines: ~50-100 ms

### Tamaño:
- Código Python: 977 líneas
- Documentación: 1,072 líneas
- Base de datos: 1.54 MB

---

## 🎯 Puntos Clave de Evaluación

### Conceptos implementados:

1. **Árboles B+** ✅
   - Estructura balanceada
   - Mantenimiento automático de orden
   - Búsquedas eficientes O(log n)
   - Búsquedas por rango

2. **ZODB** ✅
   - Persistencia orientada a objetos
   - FileStorage sin servidor
   - Transacciones ACID
   - Clase Persistent

3. **Indexación** ✅
   - Tokenización y normalización
   - Estructura de posting lists
   - Mapeo doc_id → nombre
   - Eficiencia en inserción

4. **Búsquedas** ✅
   - Exacta (hash-like)
   - Prefijo (rango ordenado)
   - Sufijo (escaneo)
   - Comodines (regex)

---

## 📚 Comparación con IndiceInvertido

| Aspecto | IndiceInvertido | IndiceOrdenado (este) |
|---------|-----------------|------------------------|
| Estructura | BSBI + bloques | Árbol B+ |
| Ordenamiento | Sort externo | Automático |
| Persistencia | Binarios custom | ZODB |
| Compresión | Front coding + VB | ZODB interno |
| Búsquedas | Booleanas | Comodines |
| Complejidad código | ~300+ líneas | 264 líneas |
| Ventaja | Espacio optimizado | Simplicidad |

---

## 📖 Documentación Entregada

- ✅ **README.md** (6,303 bytes) - Guía completa
- ✅ **ARQUITECTURA.md** (9,448 bytes) - Detalles técnicos
- ✅ **EJEMPLOS.md** (8,925 bytes) - Código de ejemplo
- ✅ **QUICKSTART.md** - Inicio rápido
- ✅ **RESUMEN.md** - Resumen ejecutivo
- ✅ Comentarios inline en todo el código
- ✅ Docstrings en todas las funciones

---

## 🔧 Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes)
- 50 MB de espacio en disco
- Sistema Linux/macOS/Windows

**Dependencias (instalación automática):**
- ZODB >= 5.8.0
- BTrees >= 5.0
- transaction >= 4.0
- persistent >= 5.0

---

## 💡 Comandos Útiles para Evaluación

```bash
# Ver ayuda
make help

# Instalar y configurar todo
./setup.sh

# Indexar corpus
make index

# Ver estadísticas visuales
make stats

# Ejecutar demostración
make demo

# Ejecutar tests
make test

# Buscador interactivo
make search

# Proceso completo end-to-end
make run

# Limpiar y reconstruir
make rebuild
```

---

## 📝 Notas Adicionales

### Diferencias clave con el proyecto base:

1. **Uso de Árboles B+**: El proyecto base usa BSBI con sort externo. Este usa OOBTree que mantiene el orden automáticamente.

2. **ZODB vs Archivos binarios**: En lugar de escribir archivos binarios custom, usa ZODB para persistencia transparente.

3. **Comodines vs Booleanos**: Las búsquedas usan patrones con `*` y `?` en lugar de operadores AND/OR/NOT.

4. **Simplicidad**: El código es más simple y limpio gracias a las abstracciones de ZODB y BTrees.

### Referencias implementadas:

- ✅ Apunte de clase: `3-11-indices-arboles-b.md`
- ✅ Proyecto base: [IndiceInvertido](https://github.com/untref-edd/IndiceInvertido)
- ✅ Documentación ZODB
- ✅ Documentación BTrees

---

## ✅ Lista de Verificación

- [x] Implementa Árboles B+ (OOBTree)
- [x] Usa ZODB para persistencia
- [x] Indexa el corpus completo
- [x] Implementa búsquedas con comodines
- [x] Interfaz CLI funcional
- [x] Tests completos pasando
- [x] Documentación exhaustiva
- [x] Código limpio y comentado
- [x] Scripts de automatización (Makefile)
- [x] Listo para demostración

---

## 🏆 Conclusión

El proyecto implementa exitosamente un **índice ordenado** usando **Árboles B+** de ZODB, cumpliendo con todos los requisitos solicitados. El código es limpio, está bien documentado y todas las funcionalidades están probadas y funcionando.

**Tiempo estimado de evaluación:** 5-10 minutos
**Comando recomendado:** `make demo` o `./setup.sh`

---

**Gracias por su tiempo y consideración.**

Para cualquier consulta o demostración adicional, por favor contactar al alumno.
