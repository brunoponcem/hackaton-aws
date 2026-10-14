---
tipo: rol
integrante: Johann
entorno: Kiro IDE Pro
frente: Reglas PGU, hitos y catálogo
---
# Johann — Reglas PGU, hitos y catálogo

**Entorno:** Kiro IDE Pro · **Color en el pipeline:** 🟩 Verde · Plan general, reglas y mapa del pipeline en [[_equipo]].

## Tareas
- [ ] **T08** · P0 · B1 · Steering de Kiro en `.kiro/steering/` que referencie [[AGENTS]], [[contexto-compartido-chileatiende]] y [[arquitectura-chileatiende]] (lo usan los 4 integrantes con Kiro) — ✅ Kiro respeta carpetas, idioma y reglas del dominio
- [ ] **T09** · P0 · B1 · Parámetros e hitos verificados en fichas oficiales → `data/catalogo/pgu.json` y `data/catalogo/hitos.json`: montos, umbral y **definición oficial de pensión base**, PFP, residencia, edad legal de vejez (el PPT dice 60 para mujeres y 65 para hombres) y apertura de la solicitud PGU (el PPT dice 64 años y 9 meses) — ✅ cada valor con `fuente_url`, vigencia y fecha de consulta; lo que no se verifique queda marcado `sin_verificar`
- [ ] **T10** · P0 · B1 · `data/catalogo/schema.json` + test que valide todos los JSON del catálogo — ✅ `pgu.json` y `hitos.json` validan
- [ ] **T11** · P0 · B2 · `evaluar_pgu(perfil, fecha_ref)` → `elegible | no_elegible | antecedente_faltante | proximo | ya_recibe`, con motivos, fuentes y **precedencia documentada** cuando hay varios motivos — ✅ test con un perfil real del dataset por cada estado; considera `estado = vigente` · depende de T02 y T09
- [ ] **T12** · P0 · B2 · `calcular_hitos`: edad legal de vejez según el perfil, apertura de la solicitud PGU, acceso a la PGU a los 65 e invitación unos 12 meses antes. Las aperturas son hitos, no vencimientos — ✅ tests con bordes (cumpleaños el mismo día, 64 años y 9 meses exactos) · depende de T09
- [ ] **T13** · P0 · B2 · Evaluación por lotes de los 500 perfiles → `reports/pgu_dataset_A.csv` + `reports/resumen.md` (estados, antecedentes faltantes, próximos hitos y a quién invitar) — ✅ cuadra con los conteos de [[datos-dataset-A]] o explica la diferencia · depende de T11 y T12
- [ ] **T14** · P1 · B3 · Otros beneficios de jubilación en el catálogo (solicitud de pensión de vejez, bono por hijo) + herramienta `buscar_beneficios` — ✅ validan contra el esquema; test por evento

## Notas
-
