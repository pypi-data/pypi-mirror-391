"""
Utilidades y validaciones
=========================

Incluye ejemplos de:

- `@staticmethod`: método sin dependencia de instancia ni clase.
- Funciones auxiliares simples (p. ej., comprobar formato de fecha).
"""

import re


class Validador:
    """Conjunto de validaciones sin estado."""

    @staticmethod
    def fecha_iso(s: str) -> bool:
        """Valida 'YYYY-MM-DD' de forma simple usando una expresión regular.

        Args:
            s (str): Cadena a validar.

        Returns:
            bool: True si coincide con el patrón, False en caso contrario.

        Nota:
            Esta validación comprueba el *formato*, no la validez del calendario
            (p. ej., no comprueba meses 1..12 ni días 1..31).
        """
        if not isinstance(s, str):
            return False
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))


def validar_fecha(s: str) -> bool:
    """Función de conveniencia que delega en `Validador.fecha_iso`.

    Args:
        s (str): Cadena con la fecha.

    Returns:
        bool: Resultado de la validación.
    """
    return Validador.fecha_iso(s)