"""Utilidades de fechas (sin dependencias externas)."""
import calendar
from datetime import date


def sumar_meses(d: date, meses: int) -> date:
    """Suma meses respetando fin de mes (29-feb + 12 meses -> 28-feb)."""
    total = d.month - 1 + meses
    anio, mes = d.year + total // 12, total % 12 + 1
    dia = min(d.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def cumple(fecha_nacimiento: date, anios: int, meses: int = 0) -> date:
    """Fecha en que la persona cumple `anios` años y `meses` meses."""
    return sumar_meses(fecha_nacimiento, anios * 12 + meses)


def edad(fecha_nacimiento: date, ref: date) -> int:
    """Edad en años cumplidos a la fecha `ref`."""
    return ref.year - fecha_nacimiento.year - (
        (ref.month, ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def meses_entre(desde: date, hasta: date) -> int:
    """Meses completos entre dos fechas (negativo si `hasta` < `desde`)."""
    m = (hasta.year - desde.year) * 12 + (hasta.month - desde.month)
    if hasta.day < desde.day:
        m -= 1
    return m


def fmt(d: date | None) -> str:
    return d.strftime("%d-%m-%Y") if d else "—"
