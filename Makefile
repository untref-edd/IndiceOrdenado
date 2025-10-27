.PHONY: help install index search stats clean rebuild test demo run

help:
	@echo "Comandos disponibles:"
	@echo "  make install   - Instalar dependencias"
	@echo "  make index     - Crear/actualizar el índice"
	@echo "  make search    - Ejecutar el buscador interactivo"
	@echo "  make demo      - Ejecutar demostración de funcionalidades"
	@echo "  make run       - Crear índice y ejecutar buscador (end-to-end)"
	@echo "  make stats     - Ver estadísticas detalladas del índice"
	@echo "  make clean     - Limpiar archivos generados"
	@echo "  make rebuild   - Limpiar y reconstruir el índice"
	@echo "  make test      - Ejecutar pruebas"

install:
	pip install -r requirements.txt

index:
	python indexar.py

search:
	python buscar.py

demo:
	python demo.py

run:
	python main.py

stats:
	python stats.py

clean:
	rm -f index/indice.fs*
	rm -f tmp/*.fs*
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

rebuild: clean index

test:
	python test_indice.py
