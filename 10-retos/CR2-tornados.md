---
tipo: reto
area: Sustentabilidad
organizacion: CR2
estado: por-evaluar
---
# Detección temprana de tornados en Chile

## Problema
Sin radares; detectar tormentas que empezarán a rotar cruzando reanálisis de vientos con imágenes GOES cada 10 min.

## Datos probables
- ERA5 (reanálisis), GOES-16/18 (disponible en AWS Open Data: s3://noaa-goes16), registro histórico de tornados

## Enfoque de IA candidato
- Clasificador espaciotemporal (CNN/ConvLSTM) sobre parches GOES + features ERA5
- Muy pocos positivos: data augmentation, anomalía

## Servicios AWS candidatos
- S3 Open Data, SageMaker, Batch, Lambda para alertas (SNS)

## Riesgos
-

## Relacionado
[[_seleccion]]
