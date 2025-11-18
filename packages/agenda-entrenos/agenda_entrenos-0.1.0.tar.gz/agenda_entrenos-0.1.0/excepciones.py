"""
Excepciones personalizadas
==========================

Definición de excepciones del dominio para proporcionar mensajes
claros de error y mantener el flujo del programa controlado.
"""


class DuracionInvalida(Exception):
    """Duración inválida (no entero o <= 0)."""

    def __init__(self, valor):
        super().__init__(f"Duración inválida: {valor}. Debe ser un entero > 0.")


class FormatoFechaInvalido(Exception):
    """Formato de fecha/entrada inválido para construir sesiones."""

    def __init__(self, texto):
        super().__init__(f"Formato inválido: {texto!r}. Esperado: 'YYYY-MM-DD;tipo;duracion'.")

class TipoSesionDesconocido(Exception):
    """Se lanza cuando el 'tipo' existe en la posición correcta pero no corresponde
    a ninguna subclase aceptada (formato ok, tipo no válido).
    """
    def __init__(self, tipo, permitidos):
        lista = ", ".join(sorted(permitidos))
        super().__init__(f"Tipo no válido: {tipo!r}. Usa uno de: {lista}")

class FirmaConstructorInvalida(Exception):
    """Se lanza cuando la llamada al constructor no respeta la firma esperada."""
    def __init__(self, clase, firma_esperada):
        super().__init__(f"Firma inválida para {clase}: {firma_esperada}")