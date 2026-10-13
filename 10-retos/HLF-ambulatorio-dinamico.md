---
tipo: reto
area: Salud
organizacion: Hospital Clínico Dra. Eloísa Díaz (HLF)
estado: por-evaluar
---
# Ambulatorio dinámico — priorización clínica y gestión de box

## Problema
Lista de espera estática mientras la condición clínica cambia; repriorizar en tiempo real y optimizar uso de boxes.

## Datos probables
- Lista de espera, diagnósticos, fechas, uso de boxes (probablemente sintéticos/anonimizados)

## Enfoque de IA candidato
- Score de riesgo (modelo tabular) + LLM para leer notas clínicas
- Optimización de agenda (OR-Tools / programación entera)

## Servicios AWS candidatos
- Bedrock, SageMaker, Lambda, DynamoDB, EventBridge

## Riesgos
-

## Relacionado
[[_seleccion]]
