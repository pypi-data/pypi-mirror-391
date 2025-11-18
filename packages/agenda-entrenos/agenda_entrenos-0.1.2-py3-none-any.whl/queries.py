"""
Consultas funcionales
=====================

Funciones puras para procesar colecciones de sesiones usando:

- `filter` (selección condicional),
- `map` (transformación),
- `reduce` (acumulación),
- y comprensiones de listas (sintaxis declarativa).

Todas las funciones esperan iterables de objetos `Sesion` (o subclases).
"""

from functools import reduce


def filtrar_por_tipo(sesiones, tipo: str):
    """Filtra sesiones por tipo de clase (`Tecnica` , `Fisica` o `Tactica').

    Args:
        sesiones (Iterable[Sesion]): Colección de sesiones.
        tipo (str): "tecnica" , "fisica" o "tactica" (no sensible a mayúsculas).

    Returns:
        list: Lista de sesiones cuyo nombre de clase coincide.

    Ejemplo:
        >>> filtrar_por_tipo([Tecnica("2025-11-10", 60)], "tecnica")
        [<Tecnica ...>]
    """
    tipo = (tipo or "").strip().lower()
    return list(filter(lambda s: s.__class__.__name__.lower() == tipo, sesiones))


def total_minutos(sesiones):
    """Suma la duración total de una colección de sesiones (reduce).

    Args:
        sesiones (Iterable[Sesion]): Colección de sesiones.

    Returns:
        int: Suma de `s.duracion` para cada sesión.
    """
    return reduce(lambda acc, s: acc + s.duracion, sesiones, 0)


def largas(sesiones, umbral=60):
    """Devuelve las sesiones con duración mayor o igual al umbral.

    Args:
        sesiones (Iterable[Sesion]): Colección de sesiones.
        umbral (int, optional): Minutos. Por defecto 60.

    Returns:
        list: Sesiones con `s.duracion >= umbral`.

    Nota:
        Implementado con **comprensión de listas**.
    """
    return [s for s in sesiones if s.duracion >= umbral]


def descripciones(sesiones):
    """Devuelve una lista de descripciones (map).

    Args:
        sesiones (Iterable[Sesion]): Colección de sesiones.

    Returns:
        list[str]: Descripciones devueltas por `s.descripcion()`.
    """
    return list(map(lambda s: s.descripcion(), sesiones))


def agrupar_por_dia(sesiones):
    """Agrupa sesiones por fecha (solo con estructuras básicas).

    Args:
        sesiones (Iterable[Sesion]): Colección de sesiones.

    Returns:
        dict[str, list]: Diccionario {fecha: [sesiones_en_esa_fecha]}

    Nota:
        Se implementa de forma explícita (sin `itertools.groupby`)
        para ajustarnos al contenido visto en clase (listas/dicts).
    """
    grupos = {}
    for s in sesiones:
        f = s.fecha
        if f not in grupos:
            grupos[f] = []
        grupos[f].append(s)
    return grupos