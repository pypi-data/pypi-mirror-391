# Hack4U Academy Courses Library

Una biblioteca Python para consultar cursos de la academia Hack4U.

## Cursos disponibles:

 - Introducción a Linux [15 horas]
 - Personalización de Entorno Linux [3 horas]
 - Introducción al Hacking [53 horas]
 - Python Ofensivo [35 horas]
 - Hacking Web [51 horas]

## Instalación

Instala el paquete usando `pip3`:

```python3
pip3 install hack4u
```

## Uso básico

### Listar todos los cursos

```python3
from hack4u import list_courses

for course in list_courses():
    print(corse)
```

### Obtener un curso por nombre

```python3
form hack4u import search_by_name

course = search_by_name("Introducción a Linux")
print(course)
```

### Calcular duración total de los cursos

```python3
form hack4u import total_duration

print(f"Duración total: {total_duration()} horas")
```