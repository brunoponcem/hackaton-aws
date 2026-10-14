---
tipo: implementacion
tarea: T03
fecha: 2026-10-14
responsable: codex
---
# T03 — Consulta autorizada del perfil

Continúa [[T02-contratos]] y [[T01-scaffold-python]]. Estado en [[board-clemente]].

`src.tools.profiles.consultar_perfil(run, *, case, repository=None)` devuelve `Profile` o `None` para un RUN válido no encontrado. `case` viene de la aplicación, nunca de los argumentos del LLM. El caso debe permitir `can_read_profile` y su RUN debe coincidir con el consultado. Antes de esa comprobación no se abre el dataset.

```python
from src.tools.profiles import consultar_perfil

# case es el caso autenticado y autorizado que entrega la API/repositorio.
profile = consultar_perfil("100.000.001-5", case=case)
```

- `normalize_run` admite puntos de miles, espacios exteriores y `k` minúscula; valida formato y DV módulo 11. No busca personas con un RUN inválido.
- `PermissionError`: autorización inexistente/no otorgada, invitación pendiente/declinada o RUN ajeno al caso. La API de T17/T21 debe resolver la identidad, la aceptación y el consentimiento; no aceptar un caso inventado por el modelo.
- `ValueError`: RUN inválido, lista de origen inválida o duplicados. Los errores de lectura y validación de datos se propagan; un archivo roto no se presenta como «persona no encontrada».
- `ProfileRepository` carga y valida una vez por instancia, de forma diferida. Puede inyectarse una ruta alternativa para tests. La ruta por defecto se resuelve desde el módulo, no desde el directorio actual.
- Las respuestas son copias profundas: modificar listas anidadas no contamina futuras consultas. No modifica el dataset ni calcula PGU. Se conserva `rsh=None` y los demás antecedentes ausentes.
- Fuente de los datos: `data/raw/dataset_A_participantes/perfiles.json` y [[datos-dataset-A]], organización del evento; perfiles sintéticos, referencia 2026-10-08. No es una conexión real a los registros del Estado.

Verificación: `uv run pytest` **40 tests pasan** (19 nuevos de T03), `uv run ruff check src tests` OK. Incluye persona existente, inexistente, RSH ausente, separación entre casos, rechazo antes de leer archivos, checksum y aislamiento de respuestas. Pendiente revisión/integración T07; T04 puede importar la herramienta.
