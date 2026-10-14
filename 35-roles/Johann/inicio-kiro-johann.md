---
tipo: setup
integrante: Johann
fecha: 2026-10-14
---
# Johann — Usar contexto acotado en Kiro

Esta preparación es **solo para el checkout de Johann**. No instala Codex/Claude, no modifica configuración global, no cambia `AGENTS.md` ni activa reglas para Clemente.

## Arranque

1. Abrir la raíz del repo en Kiro y ejecutar `uv sync`.
2. Ejecutar `uv run python 35-roles/Johann/preparar_kiro.py --check` para validar esta guía.
3. En su checkout, ejecutar `uv run python 35-roles/Johann/preparar_kiro.py --install`. Copia el contexto manual a `.kiro/steering/johann-context.md` y el filtro a `.kiroignore`. Se niega a sobrescribir archivos diferentes. Los archivos generados son configuración local: no añadirlos a commits compartidos.
4. En Kiro IDE, buscar **Agent Ignore Files** en Settings y comprobar que incluya `.kiroignore` (clave documentada `kiroAgent.agentIgnoreFiles`). Conservar otros valores de esa opción.
5. Abrir una conversación nueva y escribir `#johann-context` seguido de la tarea concreta. Si la versión no ofrece ese selector, adjuntar únicamente [[contexto-codear-johann]]. No adjuntar el repo completo ni generar resúmenes de todos los roles.

Mensaje sugerido:

> #johann-context Trabajo con Johann en Kiro desde src/app. Clemente y yo aportamos código sin reparto por tareas. Ahora quiero [objetivo inmediato]. Lee solo el contexto compacto y los archivos necesarios. Guarda mi aporte, trae origin/main, integra por merge, resuelve conflictos y duplicaciones conservando ambos aportes, verifica el conjunto y publica. Si el remoto avanzó, repite la integración sin force push. Registra el avance y no cargues el vault completo.

## Qué reduce y qué no

`inclusion: manual` permite cargar la guía solo cuando se pide. El filtro excluye documentación histórica, boards ajenos, binarios, cachés y credenciales de las herramientas compatibles; mantiene **todo `src/`, `tests/`, `data/`, `infra/` y scripts** disponible porque Johann debe entender cualquier módulo. Mantiene las guías técnicas T01–T04 y el diseño de contacto accesibles. No oculta el dataset necesario para tests, pero no conviene adjuntarlo al chat.

`AGENTS.md` se carga automáticamente en Kiro y no admite inclusión manual; esta configuración no promete eliminarlo. Evita el crecimiento adicional por importar documentos, enlaces o recursos con comodines. Si ya hay steering extenso con `inclusion: always`, pasar esos archivos a `manual` en el checkout de Johann después de revisar qué contienen; el instalador no los cambia. Tampoco puede controlar instrucciones globales o el contexto que ya acumuló una conversación.

Para agentes personalizados, seleccionar recursos puntuales en su propia configuración; no usar un glob de todo el vault o todos los steering files. Esta guía no altera agentes ajenos ni crea uno con permisos nuevos.

El filtro usa `.kiroignore` de Kiro IDE; no asumir que está disponible en Kiro Web. Si una consulta excepcional requiere una nota filtrada, quitar solo ese patrón temporalmente o adjuntar el fragmento relevante. El filtro no es una barrera de permisos ni reemplaza las reglas compartidas.

Referencias verificadas: [Steering de Kiro](https://kiro.dev/docs/steering/) y [Kiroignore](https://kiro.dev/docs/kiroignore/). No se pudo probar el comportamiento dentro del IDE de Johann desde este entorno; sí se verifica el contenido e instalación local con el script.
