from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.models.models import TipoDocumento, EstadoCita, TipoMovimiento, Moneda


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── PACIENTE ─────────────────────────────────────────────────────────────────

class PacienteCreate(BaseModel):
    nombre_completo: str
    tipo_documento: TipoDocumento = TipoDocumento.cedula_py
    numero_documento: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: str = "Paraguay"
    notas: Optional[str] = None


class PacienteUpdate(PacienteCreate):
    nombre_completo: Optional[str] = None


class PacienteOut(PacienteCreate):
    id: int
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class PacienteResumen(BaseModel):
    id: int
    nombre_completo: str
    numero_documento: Optional[str]
    telefono: Optional[str]
    fecha_nacimiento: Optional[date]

    class Config:
        from_attributes = True


# ─── HISTORIA CLÍNICA ─────────────────────────────────────────────────────────

class HistoriaCreate(BaseModel):
    paciente_id: int
    fecha: date
    motivo_consulta: str
    anamnesis: Optional[str] = None
    examen_fisico: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None
    cita_id: Optional[int] = None


class HistoriaUpdate(HistoriaCreate):
    paciente_id: Optional[int] = None
    fecha: Optional[date] = None
    motivo_consulta: Optional[str] = None


class HistoriaOut(HistoriaCreate):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ─── CITA ─────────────────────────────────────────────────────────────────────

class CitaCreate(BaseModel):
    paciente_id: int
    fecha_hora: datetime
    duracion_minutos: int = 30
    motivo: Optional[str] = None
    estado: EstadoCita = EstadoCita.agendada
    notas: Optional[str] = None


class CitaUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    duracion_minutos: Optional[int] = None
    motivo: Optional[str] = None
    estado: Optional[EstadoCita] = None
    notas: Optional[str] = None


class CitaOut(CitaCreate):
    id: int
    creado_en: datetime
    paciente_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ─── CONTABILIDAD ─────────────────────────────────────────────────────────────

class CategoriaCreate(BaseModel):
    nombre: str
    tipo: TipoMovimiento
    color: Optional[str] = "#6B7280"


class CategoriaOut(CategoriaCreate):
    id: int

    class Config:
        from_attributes = True


class MovimientoCreate(BaseModel):
    tipo: TipoMovimiento
    categoria_id: Optional[int] = None
    descripcion: str
    monto: float
    moneda: Moneda = Moneda.pyg
    fecha: date
    cita_id: Optional[int] = None

    @field_validator("monto")
    @classmethod
    def monto_positivo(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v


class MovimientoOut(MovimientoCreate):
    id: int
    creado_en: datetime
    categoria: Optional[CategoriaOut] = None

    class Config:
        from_attributes = True


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

class EstadisticasMes(BaseModel):
    mes: str
    consultas: int


class DashboardData(BaseModel):
    total_pacientes: int
    pacientes_este_mes: int
    citas_hoy: int
    ingresos_mes: float
    consultas_por_mes: list[EstadisticasMes]
    distribucion_edad: dict
