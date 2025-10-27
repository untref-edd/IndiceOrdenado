# 🚀 Inicio Rápido

## Instalación en 3 pasos

```bash
# 1. Instalar dependencias
make install

# 2. Crear el índice
make index

# 3. Ejecutar el buscador
make search
```

## O usando el script de configuración

```bash
# Ejecutar setup automático
./setup.sh
```

## Comandos principales

```bash
make help      # Ver todos los comandos disponibles
make demo      # Ver demostración completa
make stats     # Ver estadísticas del índice
make test      # Ejecutar tests
make run       # Proceso completo (indexar + buscar)
```

## Ejemplos rápidos

### Búsqueda exacta
```
Opción: 0
Término: hobbit
→ [Bombadil, Introduccion]
```

### Búsqueda por prefijo
```
Opción: 1
Prefijo: hobbi
→ hobbit: [Bombadil, Introduccion]
→ hobbits: [Bombadil, Introduccion]
```

### Búsqueda con comodines
```
Opción: 3
Patrón: h*bit
→ hobbit: [Bombadil, Introduccion]
```

## Estructura del proyecto

```
IndiceOrdenado/
├── README.md              # Documentación completa
├── ARQUITECTURA.md        # Detalles técnicos
├── EJEMPLOS.md           # Ejemplos de uso
├── indexar.py            # Creador del índice
├── buscar.py             # Interfaz de búsqueda
├── demo.py               # Demostración
├── stats.py              # Estadísticas visuales
├── main.py               # Script end-to-end
├── test_indice.py        # Tests
├── corpus/               # Documentos a indexar
├── index/                # Base de datos ZODB (generado)
│   └── indice.fs
└── tmp/                  # Archivos temporales
```

## Documentación

- **[README.md](README.md)** - Documentación completa del proyecto
- **[ARQUITECTURA.md](ARQUITECTURA.md)** - Explicación técnica detallada
- **[EJEMPLOS.md](EJEMPLOS.md)** - Ejemplos de uso prácticos

## Características principales

✅ **Árboles B+** - Estructura eficiente y ordenada  
✅ **Persistencia ZODB** - Almacenamiento en disco sin configuración  
✅ **Búsquedas con comodines** - Patrones `*` y `?`  
✅ **Interfaz CLI** - Búsquedas interactivas  
✅ **Tests completos** - Validación de funcionalidad  

## Soporte

- Ver más ejemplos en [EJEMPLOS.md](EJEMPLOS.md)
- Detalles técnicos en [ARQUITECTURA.md](ARQUITECTURA.md)
- Ejecutar `make help` para ver todos los comandos
