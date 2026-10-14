"""Citizen profile as delivered in dataset A (`perfiles.json`).

Field names are English; aliases match the dataset keys, so a raw profile
loads with `Profile.model_validate(raw)`. A missing source block is `None`
(or `[]` for pensions/benefits), as documented in the dataset README.
"""

import datetime as dt
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

RUN_PATTERN = r"^\d{7,9}-[\dK]$"


class DatasetModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid")


class Sex(StrEnum):
    FEMALE = "F"
    MALE = "M"


class LifeStatus(StrEnum):
    ALIVE = "no_fallecido"
    DECEASED = "fallecido"


class CivilRegistry(DatasetModel):
    formatted_run: str = Field(alias="run_formateado")
    first_names: str = Field(alias="nombres")
    paternal_surname: str = Field(alias="apellido_paterno")
    maternal_surname: str = Field(alias="apellido_materno")
    birth_date: date = Field(alias="fecha_nacimiento")
    sex: Sex = Field(alias="sexo")
    marital_status: str = Field(alias="estado_civil")
    has_partner: bool = Field(alias="tiene_conyuge_conviviente")
    has_children: bool = Field(alias="tiene_hijos")
    death_date: date | None = Field(alias="fecha_defuncion")
    life_status: LifeStatus = Field(alias="estado")


class SocialHouseholdRegistry(DatasetModel):
    """Registro Social de Hogares (RSH). `pfp_percentile` is simulated, not official."""

    household_id: str = Field(alias="folio_hogar")
    household_size: int = Field(alias="num_integrantes")
    relationship: str = Field(alias="parentesco")
    updated_on: date = Field(alias="fecha_actualizacion")
    cse_bracket: int = Field(alias="cse_tramo")
    household_labor_income: int = Field(alias="ingreso_trabajo_hogar")
    household_pension_income: int = Field(alias="ingreso_pensiones_hogar")
    household_capital_income: int = Field(alias="ingreso_capital_hogar")
    pfp_available: bool = Field(alias="info_pfp_disponible")
    pfp_percentile: int | None = Field(alias="pfp_percentil")


class MovementType(StrEnum):
    ENTRY = "entrada"
    EXIT = "salida"


class MigrationMovement(DatasetModel):
    date: dt.date = Field(alias="fecha")
    type: MovementType = Field(alias="tipo")


class ResidenceResult(StrEnum):
    MEETS = "cumple"
    DOES_NOT_MEET = "no_cumple"


class Residence(DatasetModel):
    current_residence: str = Field(alias="residencia_actual")
    period_from: date = Field(alias="periodo_evaluado_desde")
    period_to: date = Field(alias="periodo_evaluado_hasta")
    total_entries: int = Field(alias="total_entradas")
    total_exits: int = Field(alias="total_salidas")
    days_abroad_last_5_years: int = Field(alias="dias_fuera_pais_ultimos_5")
    years_since_age_20: float = Field(alias="anios_residencia_desde_20")
    years_last_5: float = Field(alias="anios_residencia_ultimos_5")
    result: ResidenceResult = Field(alias="resultado")
    movements: list[MigrationMovement] = Field(default_factory=list, alias="movimientos")


class ContributionStatus(StrEnum):
    PAID = "con_cotizacion"
    UNPAID = "sin_cotizacion"


class Contribution(DatasetModel):
    period: str = Field(alias="periodo", pattern=r"^\d{4}-\d{2}$")
    amount: int = Field(alias="monto")
    taxable_income: int | None = Field(alias="remuneracion_imponible")
    status: ContributionStatus = Field(alias="estado")


class PensionFund(DatasetModel):
    """AFP affiliation. `estimated_self_funded_pension` (PAFE) is simulated."""

    afp: str
    cutoff_date: date = Field(alias="fecha_corte")
    fund: str = Field(alias="fondo")
    months_with_contribution: int = Field(alias="cotizaciones_con")
    months_without_contribution: int = Field(alias="cotizaciones_sin")
    taxable_income: int | None = Field(alias="remuneracion_imponible")
    estimated_self_funded_pension: int | None = Field(alias="pafe_estimada")
    contributions: list[Contribution] = Field(default_factory=list, alias="cotizaciones")


class RecordType(StrEnum):
    PENSION = "pension"
    IPS_BENEFIT = "beneficio_ips"


class RecordStatus(StrEnum):
    ACTIVE = "vigente"
    ENDED = "terminado"
    SUSPENDED = "suspendido"


class PensionOrBenefit(DatasetModel):
    record_id: str = Field(alias="id_registro")
    record_type: RecordType = Field(alias="tipo_registro")
    pension_type: str | None = Field(alias="tipo_pension")
    benefit_type: str | None = Field(alias="tipo_beneficio")
    amount: int = Field(alias="monto")
    payer: str = Field(alias="entidad_pagadora")
    is_survivor_pension: bool = Field(alias="pension_sobrevivencia")
    is_ips_benefit: bool = Field(alias="beneficio_ips")
    status: RecordStatus = Field(alias="estado")


class EmploymentStatus(DatasetModel):
    currently_working: bool = Field(alias="trabaja_actualmente")
    start_date: date | None = Field(alias="fecha_inicio")
    end_date: date | None = Field(alias="fecha_termino")


class Profile(DatasetModel):
    """One person from `perfiles.json`. `None` means the source has no record."""

    run: str = Field(pattern=RUN_PATTERN)
    civil_registry: CivilRegistry = Field(alias="registro_civil")
    rsh: SocialHouseholdRegistry | None = None
    residence: Residence | None = Field(default=None, alias="residencia")
    pension_fund: PensionFund | None = Field(default=None, alias="prevision")
    pensions_benefits: list[PensionOrBenefit] = Field(
        default_factory=list, alias="pensiones_beneficios"
    )
    employment: EmploymentStatus | None = Field(default=None, alias="situacion_laboral")
