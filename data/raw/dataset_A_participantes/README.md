# Dataset A – Participantes (Jubilación + PGU)

Datos 100% sintéticos. Semilla 20261008. Fecha de referencia 2026-10-08. 500 personas.

## Archivos (se unen por `run`)
| Archivo | Filas | ¿Quién aparece? |
|---|---|---|
| `registro_civil.csv` | 500 | Las 500 personas (tabla maestra) |
| `rsh.csv` | 497 | Personas con Registro Social de Hogares |
| `residencia.csv` | 497 | Personas con registro de residencia/movimientos |
| `movimientos_migratorios.csv` | 1417 | Una fila por entrada/salida (últimos 5 años + llegada al país si es inmigrante) |
| `prevision.csv` | 412 | Afiliados a AFP |
| `prevision_cotizaciones.csv` | 4944 | 12 filas por afiliado (2025-10 a 2026-09) |
| `pensiones_beneficios.csv` | 75 | Una fila por pensión o beneficio IPS |
| `situacion_laboral.csv` | 485 | Personas con información laboral |
| `perfiles.json` | 500 | Un objeto por persona con todos los bloques (null / [] si no aparece en el origen) |

## Qué significa no aparecer en un origen
| Origen | Ausencia significa | ¿Antecedente faltante? |
|---|---|---|
| registro_civil | — (siempre está) | — |
| rsh | No tiene Registro Social de Hogares | Sí: no se puede evaluar el PFP |
| residencia | Sin registro de movimientos migratorios | Sí: no se puede evaluar residencia |
| prevision | Nunca estuvo afiliado a AFP | No |
| pensiones_beneficios | No recibe pensiones ni beneficios | No (pensión = $0) |
| situacion_laboral | Sin información laboral | No bloquea PGU |

## Notas
- RUN de 9 dígitos con DV válido (módulo 11): fuera del rango asignado hoy, no pertenecen a nadie.
- AFP, compañías e identificadores de hogar son ficticios. No se identifica empleador.
- `pafe_estimada` (en prevision) es un valor simulado, no un cálculo actuarial.
- `pfp_percentil` es una simulación del PFP (no la fórmula oficial de la Res. Ex. N° 77).
- Montos en CLP mensuales. Valores PGU según ficha ChileAtiende consultada el 08-10-2026.
