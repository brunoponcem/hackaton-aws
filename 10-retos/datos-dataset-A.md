---
tipo: datos
reto: "[[ChileAtiende-a-tiempo]]"
fecha: 2026-10-14
origen: dataset_A_participantes.zip (organización)
ubicacion: data/raw/dataset_A_participantes/
---
# Dataset A — Participantes (Jubilación + PGU)

Entregado por la organización. Son datos **100% sintéticos**: 500 personas, semilla 20261008 y **fecha de referencia 2026-10-08**. Los RUN tienen DV válido pero están fuera del rango asignado. El zip original quedó en la raíz del repo y se descomprimió en `data/raw/dataset_A_participantes/`.

> Implicancia principal: el dataset está diseñado para el evento de vida **jubilación** y la **Pensión Garantizada Universal (PGU)**. El MVP pasa a centrarse en eso (ver [[0004-mvp-jubilacion-pgu]]).

## Archivos (se unen por `run`)
| Archivo | Filas | Contenido | Si la persona no aparece |
|---|---|---|---|
| `registro_civil.csv` | 500 | Tabla maestra: nombre, fecha de nacimiento, sexo, estado civil, hijos, defunción | — (siempre está) |
| `rsh.csv` | 497 | Registro Social de Hogares: folio, integrantes, tramo CSE, ingresos del hogar, `pfp_percentil` | **Antecedente faltante**: no se puede evaluar el PFP |
| `residencia.csv` | 497 | Años de residencia desde los 20 y en los últimos 5, días fuera del país, `resultado` cumple/no_cumple | **Antecedente faltante**: no se puede evaluar la residencia |
| `movimientos_migratorios.csv` | 1417 | Entradas y salidas (últimos 5 años + llegada si es inmigrante) | — |
| `prevision.csv` | 412 | AFP, fondo, cotizaciones de 12 meses, remuneración, `pafe_estimada` | Nunca estuvo afiliado (no bloquea) |
| `prevision_cotizaciones.csv` | 4944 | 12 períodos por afiliado (2025-10 a 2026-09) | — |
| `pensiones_beneficios.csv` | 75 | Pensiones (vejez, sobrevivencia, sistema antiguo) y beneficios IPS (PGU), con monto y estado | No recibe nada: pensión = $0 |
| `situacion_laboral.csv` | 485 | Si trabaja, fechas de inicio y término | No bloquea la PGU |
| `perfiles.json` | 500 | Un objeto por persona con todos los bloques anteriores (`null` / `[]` si no aparece) | — |

**Para el agente, `perfiles.json` es suficiente**: una persona = un objeto, listo para la herramienta `consultar_perfil(run)`.

## Perfil rápido (calculado al 2026-10-08)
- Edades de 20 a 88 años. 20 fallecidos y 480 vivos.
- **58 personas vivas de 65 años o más**, de las cuales **56 no tienen PGU registrada**.
  - 4 tienen un antecedente faltante (sin RSH, sin residencia o sin información de PFP).
  - 37 cumplen residencia y tienen PFP ≤ 90. Son candidatas a PGU no cobrada, pero falta revisar el requisito de pensión base.
- **17 personas cumplen 65 en los próximos 12 meses**. Son el caso "a tiempo": avisarles antes de que cumplan.
- 52 personas tienen entre 60 y 64 años.
- Residencia: 270 cumplen y 227 no. Hay 3 personas residiendo en el extranjero.
- `pfp_percentil > 90` (10% más rico): 55 personas.
- Hay 8 registros de PGU, algunos en estado `terminado`. Hay que mirar `estado`, no solo la existencia del registro.
- `pafe_estimada` viene en 183 afiliados. Es un valor **simulado** de pensión autofinanciada (no actuarial).

Estos números salen de un cálculo rápido sin reglas oficiales. Son orientativos hasta que existan las herramientas con tests.

## Requisitos PGU que el dataset permite evaluar
Hay que contrastarlos con la ficha ChileAtiende de la PGU. El README dice que los montos se tomaron de esa ficha el 08-10-2026, pero **el dataset no incluye una tabla de parámetros**, así que los montos y umbrales deben cargarse en el catálogo desde la ficha oficial.

| Requisito | Campo del dataset |
|---|---|
| Edad ≥ 65 | `registro_civil.fecha_nacimiento` (vs. fecha de referencia) |
| Estar vivo | `registro_civil.estado` |
| No pertenecer al 10% más rico (PFP) | `rsh.pfp_percentil`, `rsh.info_pfp_disponible` |
| Residencia en Chile (20 años desde los 20 y 4 de los últimos 5) | `residencia.anios_residencia_desde_20`, `anios_residencia_ultimos_5`, `resultado` |
| Pensión base bajo el umbral | Suma de `pensiones_beneficios.monto` vigentes (pensión = $0 si no aparece) |
| No tener PGU vigente | `pensiones_beneficios` con `tipo_beneficio = PGU` y `estado = vigente` |

Ojo: `pfp_percentil` es una simulación, no la fórmula oficial (Res. Ex. N° 77). Para la demo se usa tal cual.

## Resultados posibles por persona (propuesta)
- `elegible`: cumple todo → ruta para solicitar la PGU.
- `no_elegible`: incumple un requisito → explicar cuál y, si existe, mostrar una alternativa.
- `antecedente_faltante`: falta RSH, residencia o PFP → ruta para conseguir el antecedente (por ejemplo, ingresar al RSH) y luego reevaluar.
- `proximo`: cumple 65 dentro de N meses → aviso anticipado con lo que debe tener listo.
- `ya_recibe`: tiene PGU vigente.

## Pendientes
- [ ] Preguntar a los mentores si habrá un dataset B o más (el nombre "A" sugiere que sí) y cómo se evalúa el uso de estos datos.
- [ ] Cargar los parámetros de la PGU (montos y umbrales vigentes) desde la ficha ChileAtiende con `fuente_url`.
- [x] `data/raw/` se versiona en git (decidido el 2026-10-14).

## Relacionado
[[ChileAtiende-a-tiempo]] · [[arquitectura-chileatiende]] · [[0004-mvp-jubilacion-pgu]] · [[board]]
