---
tipo: implementacion
tarea: T01
fecha: 2026-10-14
responsable: codex
---
# T01 — Base Python y cliente Bedrock

Contexto: [[Clemente]], [[_equipo]], [[board]] y [[0003-orquestacion-agente]]. Implementación en `codex/T01`; revisión e integración a `main` mediante T07.

## Qué incluye
- `pyproject.toml`: Python 3.12, dependencias boto3 y python-dotenv, herramientas de desarrollo pytest y ruff. `.python-version` fija 3.12 y `uv.lock` registra versiones resueltas.
- Paquetes iniciales `src`, `src.agent` y `src.tools`. Se instalan con setuptools para importar `src.agent.bedrock` desde cualquier directorio después de `uv sync`. Los contratos y módulos de otros frentes se agregan en sus propias tareas.
- `BedrockSettings.from_env()` lee `.env` desde el directorio actual, o una ruta explícita; las variables de proceso tienen prioridad. No modifica el entorno global.
- Modelo por defecto Sonnet 5, región por defecto `us-east-1`. Si `AWS_REGION` no está definido, también se acepta `AWS_DEFAULT_REGION`. Modelo/perfil/región vacíos usan sus valores por defecto; sin perfil se utiliza la cadena normal de credenciales de boto3 (incluido rol IAM).
- `BedrockClient.from_env()` crea el cliente `bedrock-runtime`; `converse(messages, **options)` usa siempre el modelo configurado y devuelve la respuesta completa, incluido tool use. Valida la allowlist de [[AGENTS]] antes de crear la sesión AWS.
- No hay llamadas AWS al importar módulos. Crear un cliente real puede requerir credenciales válidas. Los errores AWS se propagan para que el bucle de T04 los maneje; no se generan respuestas de dominio en el cliente.

## Ejecución local
Desde la raíz: `uv sync`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`. No se necesita acceso AWS para estas verificaciones. Si falta `.env`, copiar `.env.example`; nunca sobrescribir uno existente.

Uso para T04 (la llamada sí consume una inferencia y requiere AWS):

```python
from src.agent.bedrock import BedrockClient

client = BedrockClient.from_env()
response = client.converse(
    messages=[{"role": "user", "content": [{"text": "Hola"}]}],
    inferenceConfig={"maxTokens": 128},
)
```

En un despliegue con rol IAM, no configurar `AWS_PROFILE`; mantener región y `BEDROCK_MODEL_ID` como variables de entorno. Las credenciales no se incluyen en el código ni en la nota.

## Verificación y límites
Verificación ejecutada con Python 3.12.13: `uv sync` completado; `uv run pytest` **11 passed**; `uv run ruff check .` y `uv run ruff format --check .` sin errores. No se hicieron inferencias reales ni se modificó `.env`.

`tests/test_bedrock.py` cubre lectura de dotenv, prioridad del entorno, valores vacíos, región alternativa, rechazo de modelos no permitidos, creación de sesión, envío de Converse con herramientas y propagación de errores. Los tests usan mocks y `botocore.stub.Stubber`, con credenciales ficticias y sin invocar AWS.

Referencia de implementación: [documentación oficial de Converse en boto3](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/converse.html). Se conserva la respuesta completa para el futuro bucle de herramientas de T04.

T01 no implementa contratos (T02), consulta del perfil (T03), reglas PGU ni bucle del agente (T04). El criterio de aceptación final exige estas verificaciones en `main` después de revisión/integración T07; no se marca terminado en `main` solo por pasar en la rama.
