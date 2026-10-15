# Capa de contacto sintética

`contacto.csv` contiene 500 contactos **ficticios**, uno por RUN de `data/raw/dataset_A_participantes/perfiles.json`. Generados con semilla **20261008** por `src/app/ruta/contacto.py`; no se modificó el dataset original.

- Email `@example.com` y teléfono `SIM-TEL-...` no destinado a llamadas. Una fracción de los campos está vacía para probar saltos de etapa.
- Empleador ficticio únicamente si el perfil registra trabajo actual.
- Región/provincia/comuna se asignan aleatoriamente entre seis combinaciones ilustrativas reales; **no corresponden al domicilio de la persona ni a una distribución poblacional**. Referencia territorial: [Códigos Únicos Territoriales de SUBDERE](https://www.subdere.gov.cl/documentacion/c%C3%B3digos-%C3%BAnicos-territoriales-actualizados-al-06-de-septiembre-2018).
- `synthetic=True` identifica la capa de demo. La edad y las condiciones para seleccionar candidatos provienen del dataset y del motor existente, no del archivo de contacto.

El CLI crea el archivo solo si no existe; nunca lo sobrescribe. Para generar otra semilla de contactos, usar un archivo nuevo con `--contacts`. En la UI se generan contactos en memoria según la semilla elegida y se guardan dentro del snapshot SQLite.

Uso y límites en [[backend-embudo-contacto]]. No se envían mensajes a estas direcciones ni se integra un proveedor de llamadas.
