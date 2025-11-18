"""
Core (POO)
==========

Define el modelo orientado a objetos de la librería.

- `Sesion` es una clase abstracta (abstracción) con interfaz común.
- `Tecnica` y `Fisica` heredan de `Sesion` (herencia) y redefinen `descripcion` (polimorfismo).
- `duracion` está encapsulado usando `@property` + setter (encapsulación).
- `Sesion.desde_cadena` es un `@classmethod` que actúa como constructor alternativo.

Este módulo no necesita librerías externas.
"""

from abc import ABC, abstractmethod
from excepciones import DuracionInvalida, FormatoFechaInvalido, TipoSesionDesconocido, FirmaConstructorInvalida
from utils import validar_fecha


class Sesion(ABC):
    """Sesión base de entrenamiento (clase abstracta).

    Args:
        fecha (str): Fecha en formato 'YYYY-MM-DD'.
        duracion (int): Duración en minutos (> 0).

    Raises:
        FormatoFechaInvalido: Si la fecha no respeta el formato.
        DuracionInvalida: Si la duración no es `int` o es <= 0.
    """

    def __init__(self, *args):

        firma = f"{self.__class__.__name__}(fecha: str, duracion: int)"

        # --- Comprobación de ARIDAD POSICIONAL ---
        if len(args) != 2:
            raise FirmaConstructorInvalida(self.__class__.__name__, firma)
        
        fecha, duracion = args
        
        # Validación de fecha (utilidad estática)
        if not validar_fecha(fecha):
            raise FormatoFechaInvalido(fecha)

        # Guardamos fecha como atributo protegido (lectura sin setter)
        self._fecha = fecha

        # Encapsulación: duración privada con validación en setter
        self.__duracion = None  # será establecido a través del setter
        self.duracion = duracion

    # ---------- Encapsulación con @property ----------
    @property
    def duracion(self) -> int:
        """int: Duración de la sesión en minutos (> 0)."""
        return self.__duracion  # atributo privado

    @duracion.setter
    def duracion(self, minutos: int) -> None:
        """Setter de duración con validación.

        Args:
            minutos (int): minutos > 0

        Raises:
            DuracionInvalida: Si `minutos` no es `int` o es <= 0.
        """
        if not isinstance(minutos, int) or minutos <= 0:
            raise DuracionInvalida(minutos)
        self.__duracion = minutos

    @property
    def fecha(self) -> str:
        """str: Fecha 'YYYY-MM-DD' (solo lectura)."""
        return self._fecha

    # ---------- Abstracción ----------
    @abstractmethod
    def descripcion(self) -> str:
        """Descripción corta de la sesión.

        Returns:
            str: Descripción legible.
        """
        ...

    # ---------- Constructor alternativo con @classmethod ----------
    @classmethod
    def desde_cadena(cls, s: str) -> "Sesion":
        # Formato esperado: 'YYYY-MM-DD;tipo;duracion'
        firma = "Sesion.desde_cadena('YYYY-MM-DD;tipo;duracion')"
        try:
            partes = s.split(";")
            if len(partes) != 3:
                # Faltan/sobran campos -> error de firma
                raise FirmaConstructorInvalida(cls.__name__, firma)

            # Normalizamos espacios
            fecha, tipo, dur_str = (p.strip() for p in partes)

            # dur debe ser convertible a int -> si no, error de firma
            try:
                dur = int(dur_str)
            except ValueError as e:
                raise FirmaConstructorInvalida(cls.__name__, firma) from e

        except FirmaConstructorInvalida:
            # Re-emitimos tal cual para no reconvertir a FormatoFechaInvalido
            raise
        except Exception:
            # Cualquier otro problema de parseo inesperado -> formato inválido
            raise FormatoFechaInvalido(s)

        # Validación de fecha (igual que antes)
        if not validar_fecha(fecha):
            raise FormatoFechaInvalido(s)

        tipo = tipo.lower()

        # Mapeo explícito de tipos permitidos (incluyendo 'tactica')
        mapping = {
            "tecnica": Tecnica,
            "fisica":  Fisica,
            "tactica": Tactica,
        }

        SubClase = mapping.get(tipo)
        if SubClase is None:
            # Formato correcto, pero tipo no soportado
            raise TipoSesionDesconocido(tipo, mapping.keys())

        # Construcción final (exactamente dos posicionales)
        return SubClase(fecha, dur)


class Tecnica(Sesion):
    """Sesión de carácter técnico (ejercicios con balón, táctica individual, etc.)."""

    def descripcion(self) -> str:
        """str: Descripción legible especializada."""
        return f"[Técnica] {self.fecha} · {self.duracion} min"


class Fisica(Sesion):
    """Sesión de carácter físico (resistencia, fuerza, velocidad…)."""

    def descripcion(self) -> str:
        """str: Descripción legible especializada."""
        return f"[Física] {self.fecha} · {self.duracion} min"
    
class Tactica(Sesion):
    """Sesión de carácter táctico """

    def descripcion(self) -> str:
        """str: Descripción legible especializada."""
        return f"[Táctica] {self.fecha} · {self.duracion} min"