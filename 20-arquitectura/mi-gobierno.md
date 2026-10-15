# Mi Gobierno

Beneficios incorpora el Asistente de ayuda compartido al lado del listado. Usa el perfil seleccionado y el mismo motor/consentimiento que la ruta; antes de autorizar solo recibe el contexto permitido. Datos personales no renderiza otro chatbot. La guía de un beneficio conserva su asistente.

El panel de ayuda ocupa el 40% del espacio entre columnas tanto en Beneficios como en la guía PGU. El campo para escribir está justo debajo del título y la descripción del asistente, antes de la conversación (420 px de alto), para poder preguntar sin bajar por el historial. A pedido del usuario se retiraron las preguntas frecuentes de Mi Gobierno. Hasta 1050 px de pantalla se apila bajo el contenido principal y ocupa el ancho disponible. Verificado en Chrome a 1440, 900 y 390 px, sin desbordamiento horizontal; acceso a la guía OK. Suite de 146 pruebas y verificador de 500 perfiles OK.

**Navegación vigente:** Mi Gobierno abre en Beneficios. Datos personales es una vista separada con las cinco secciones y todos los tipos de adjuntos. Cada beneficio despliega sus requisitos y permite adjuntar los documentos de apoyo faltantes allí mismo.

Los archivos se guardan una sola vez por persona y tipo de documento, independientemente del lugar de carga. PGU, FUAS, gratuidad y becas consultan ese repositorio compartido: el archivo existente aparece disponible, sin pedir otra subida. Reemplazar o eliminar afecta a todos los beneficios que lo usan. Se agregaron comprobante FUAS, matrícula, antecedentes académicos y certificado de residencia al catálogo de documentos personales. La disponibilidad del archivo no equivale a validación ni altera la elegibilidad.

Tus datos se organiza en 01 Identidad personal, 02 Domicilio y contacto, 03 Documentos, 04 Información laboral y 05 Previsión y salud. Se conservan el carnet y controles de privacidad; los adjuntos quedan en Documentos. Profesión, ocupación y actividad económica se guardan como declaraciones. Previsión y salud exige consentimiento y una acción de mostrar datos; no se inventa sistema de salud cuando no existe en el dataset.

El resumen junto al carnet muestra domicilio, comuna, región, correo, teléfono y estado civil en lugar de estados de cédula/licencia. Domicilio, comuna, región, email y teléfono salen de la **misma fuente que el colador** (`ruta.ficha.contact_for`): el contacto que usó la campaña si la persona está en ella, y si no, la capa sintética. Si falta un canal, se muestra «Sin información». Antes el email se armaba con el nombre y el teléfono era fijo, lo que no coincidía con el colador. Ver [[ficha-beneficiario]].

Para completar la maqueta, nacionalidad se muestra como CHILENA; emisión y vencimiento ausentes usan las fechas ficticias 15 OCT 2025 y 15 OCT 2035. La firma de ejemplo se compone tipográficamente del nombre y apellido sintéticos. Se conserva la etiqueta DEMO; estos valores no alimentan validaciones documentales.

El perfil de demostración muestra nacionalidad Chilena por solicitud del usuario. Se retiró la leyenda inferior y se conserva DEMO en la esquina. RUN (también en el resumen), número de documento y nacimiento aparecen como `****`, con controles de ojo accesibles para revelar/ocultar cada campo. Es una ocultación visual del lado del navegador, no cifrado ni control de autorización; no modifica el consentimiento ni el motor de beneficios.

El carnet incluye todos los campos de la referencia: apellidos, nombres, nacionalidad, sexo, fecha de nacimiento, número de documento, fecha de emisión, fecha de vencimiento, firma del titular y RUN. Los campos ausentes del dataset se muestran como «Sin información»; no se inventan fechas, nacionalidad ni firmas.

El carnet minimalista toma distribución y paleta del ejemplo `assets/El_ejemplo_de_Cedula_identidad_Chile_2013.jpg`: retrato a la izquierda, datos a la derecha, encabezado azul y fondo celeste suave. Es HTML/CSS con datos dinámicos, silueta ilustrativa y marca de documento ficticio; no copia fotografía, firma, sellos ni mecanismos de seguridad del ejemplo. El número de documento no consultado se indica expresamente.

La acción superior derecha es ahora un botón directo «Revocar autorización». Abre un solo diálogo modal de confirmación, sin un menú «Mis permisos» previo. Cancelar o cerrar el diálogo conserva los datos; solo la confirmación elimina los adjuntos y revoca el consentimiento.

Mis permisos se abre desde la esquina superior derecha de Tus datos. Revocar requiere dos acciones: solicitar revocación y confirmar expresamente la eliminación. La confirmación advierte que se borran documentos y declaración económica y que habrá que adjuntarlos otra vez. Cancelar conserva datos y autorización.

En Tus datos, los adjuntos se presentan como cinco casillas independientes: cédula, licencia, RSH, comprobante de ingresos y antecedentes. Cada una permite adjuntar, reemplazar y eliminar su archivo sin seleccionar el tipo en un formulario general. La situación económica se edita en el mismo bloque, antes del listado de beneficios.

El listado apila PGU, FUAS, gratuidad y becas de educación superior. Las tres entradas educativas muestran «Faltan datos para verificar» y permiten abrir sus antecedentes por confirmar y fuente Mineduc. FUAS se identifica como formulario, no pago. No se infiere elegibilidad estudiantil del perfil previsional; el catálogo se amplía con `EDUCATION_OPTIONS` y exige reglas oficiales antes de habilitar solicitudes personalizadas.

**Presentación vigente:** primero Tus datos con el carnet ficticio y después una lista compacta de beneficios. Se retiraron bienvenida, etiqueta de cuenta, tarjetas de montos/resumen y pestañas. Datos editables, adjuntos, otros apoyos y permisos quedan en desplegables; requisitos y detalle se consultan desde cada beneficio.

La identidad se muestra como un carnet de demostración con nombres, apellidos, RUN, fecha de nacimiento y sexo del perfil seleccionado. Usa una silueta y marca visible «DOCUMENTO FICTICIO · SIN VALIDEZ»; no incorpora sellos, firma ni códigos de verificación oficiales.

La portada pública sigue siendo ChileAtiende. El encabezado y la invitación de Inicio llevan a **Mi Gobierno**, un espacio personal de demostración. El agente ya no aparece en Inicio; acompaña la ruta de un beneficio.

## Recorrido disponible

1. Elegir un perfil sintético en la barra lateral (sin integración con ClaveÚnica).
2. Aceptar explícitamente el acompañamiento y autorizar la consulta de antecedentes. Sin permiso no se muestran RSH, pensiones ni resultados personalizados.
3. Consultar Mis beneficios, Mi información y Mis documentos. Identidad viene del dataset; vigencia de cédula y licencia no se inventan.
4. Guardar situación laboral, ingresos, integrantes y antecedentes declarados. Adjuntar PDF/JPG/PNG de hasta 10 MB por tipo de documento. Adjuntos y declaración quedan en SQLite local, nunca versionados ni enviados al LLM.
5. Abrir «Cobrar beneficio» únicamente con PGU elegible según el motor existente. Faltantes abren «Completar antecedentes», edad próxima abre preparación y los incumplimientos bloquean el cobro. Se explican los requisitos que originaron el resultado.
6. Seguir una ruta con las dependencias de PGU y sus antecedentes, manteniendo los IDs/historial existentes. La persona confirma sus pasos; resolución y pago requieren al organismo. No hay envío de solicitudes, pago real ni agente que opere portales externos.

La declaración de ingresos, el tramo CSE y el archivo RSH no se convierten automáticamente en PFP ni en evidencia validada. Adjuntar un archivo no concede el beneficio. El botón abre la guía para la solicitud, no acredita un pago aprobado. El monto mostrado es orientativo y usa la fecha de referencia/parámetros del prototipo.

## Alcance del catálogo

La evaluación personalizada integra PGU, no todos los beneficios chilenos. Becas y otros apoyos aparecen como **sin evaluar**, con enlaces al catálogo oficial; no se presentan como beneficios concedidos. Un catálogo futuro necesita fuentes oficiales, reglas versionadas por vigencia y cobertura de requisitos, además del scraping de fichas. No basta con una lista producida por un LLM.

Referencias consultadas el 15-10-2026:
- [PGU, ChileAtiende](https://www.chileatiende.gob.cl/fichas/102077).
- [Ventanilla Única Social](https://www.ventanillaunicasocial.gob.cl/).
- [Becas de arancel, Mineduc](https://portal.beneficiosestudiantiles.cl/becas/becas-de-arancel).

## Persistencia y verificación

`ruta/government.py` agrega tablas de declaraciones y documentos en `config.DB_PATH`. Los archivos se validan por extensión, firma y tamaño; se guardan como BLOB local con hash y nombre saneado. Es una demo sin autenticación real, no un repositorio de documentos de producción. La revocación desde Mi Gobierno elimina esos adjuntos/declaraciones; la lectura y escritura siempre exigen el consentimiento actual. Reiniciar la demo elimina ambas tablas personales.

139 pruebas y verificador de 500 perfiles pasan. Se cubren todos los estados PGU, dependencias de ruta, consentimiento, carga inválida/tamaño, declaraciones sin alterar elegibilidad, navegación, pasos y revocación. Ver [[0013-mi-gobierno]] y [[portada-chileatiende]]. El proceso de contacto conserva el backend existente; su siguiente integración de experiencia queda aparte.
