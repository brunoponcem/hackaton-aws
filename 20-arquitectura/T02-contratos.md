---
tipo: diseño
tarea: T02
dueño: Clemente (Claude)
fecha: 2026-10-14
---
# T02 — Contratos compartidos (`src/contracts/`)

Modelos pydantic que **todos importan**. Nadie define su propia versión de un caso, un perfil o un resultado: si falta un campo, se pide a Clemente ([[_equipo]]).

```python
from src.contracts import Profile, PguResult, PguStatus, Milestone, Case, Channel
```

Los identificadores van en inglés ([[AGENTS]]). Los **valores** de los enums quedan en español, porque son los que se ven en la API, el JSON y la interfaz.

## Equivalencias con el reparto de tareas
| En el plan | Modelo | Módulo |
|---|---|---|
| Perfil | `Profile` (+ `CivilRegistry`, `SocialHouseholdRegistry`, `Residence`, `PensionFund`, `PensionOrBenefit`, `EmploymentStatus`) | `profile.py` |
| ResultadoPGU | `PguResult` (+ `PguStatus`, `Reason`, `Requirement`) | `evaluation.py` |
| Hito | `Milestone` (+ `MilestoneKind`) | `evaluation.py` |
| Fuente | `Source` | `evaluation.py` |
| Invitacion | `Invitation` (+ `InvitationResponse`) | `case.py` |
| Autorizacion | `Authorization` | `case.py` |
| PasoRuta | `RouteStep` | `case.py` |
| ChecklistItem | `ChecklistItem` (+ `ChecklistStatus`) | `case.py` |
| Mensaje | `Message` (+ `MessageRole`, `Channel`) | `case.py` |
| Caso | `Case` | `case.py` |

## Decisiones
- **El perfil carga directo del dataset**: los alias coinciden con las claves de `perfiles.json`, así que basta con `Profile.model_validate(raw)`. Un bloque ausente es `None` (o `[]` en pensiones), como indica el README del dataset. El test carga los 500 perfiles.
- **El RUN se guarda normalizado**: `12345678-K`, sin puntos. Normalizar lo que escribe la persona es parte de T03.
- **`PguResult.preliminary` siempre es `True`**: el contrato no permite presentar una orientación como adjudicación de PGU.
- **`PguStatus`**: `elegible`, `no_elegible`, `antecedente_faltante`, `proximo`, `ya_recibe`. Cada `Reason` indica el requisito, si se cumple (`None` si no se pudo evaluar) y su `Source`. La precedencia entre estados la define T11.
- **`Milestone.is_deadline` es `False` por defecto**: la apertura de la solicitud PGU es un hito, no un vencimiento.
- **`Source.verified`**: es `False` mientras el valor no se contraste con la ficha oficial (T09).
- **`Case.can_read_profile`**: es `True` solo si la invitación fue aceptada (o no hubo invitación) **y** hay una autorización otorgada. T03, T17 y T21 deben consultarlo antes de leer el perfil ampliado.
- **Perfil y resultado son inmutables** (`frozen`). El caso es mutable y valida cada asignación, porque se va completando durante la conversación.

## Cómo probar
```
uv run pytest tests/test_contracts.py
```
