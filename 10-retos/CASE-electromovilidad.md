---
tipo: reto
area: Sustentabilidad
organizacion: CASE
estado: descartado
---
# Electromovilidad eficiente

## Problema
Optimizar rutas de flotas eléctricas con restricciones de autonomía y carga.

## Datos probables
- Trayectorias GPS de flotas, ubicación de cargadores, consumo

## Enfoque de IA candidato
- VRP con restricciones de energía (OR-Tools) + modelo de consumo
- LLM como interfaz para el planificador

## Servicios AWS candidatos
- Amazon Location Service, SageMaker, Lambda, Bedrock

## Riesgos
-

## Relacionado
[[_seleccion]]
