from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Integer, Date, DateTime, Text, Numeric,
    ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base


class TipoDocumento(str, enum.Enum):
    cedula_py = "cedula_py"   # Cédula paraguaya
    rg_br = "rg_br"           # RG brasileño
    cpf_br = "cpf_br"         # CPF brasileño
    pasaporte = "pasaporte"


class EstadoCita(str, enum.Enum):
    agendada = "agendada"
    confirmada = "confirmada"
    realizada = "realizada"
    cancelada = "cancelada"
    no_asistio = "no_asistio"


class TipoMovimiento(str, enum.Enum):
    ingreso = "ingreso"
    gasto = "gasto"


class Moneda(str, enum.Enum):
    pyg = "PYG"
    usd = "USD"
    brl = "BRL"


# ─── USUARIO ─────────────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─── PACIENTE ─────────────────────────────────────────────────────────────────

class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        SAEnum(TipoDocumento), default=TipoDocumento.cedula_py
    )
    numero_documento: Mapped[Optional[str]] = mapped_column(String(30))
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date)
    sexo: Mapped[Optional[str]] = mapped_column(String(20))
    telefono: Mapped[Optional[str]] = mapped_column(String(30))
    correo: Mapped[Optional[str]] = mapped_column(String(200))
    direccion: Mapped[Optional[str]] = mapped_column(Text)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100))
    pais: Mapped[str] = mapped_column(String(50), default="Paraguay")
    notas: Mapped[Optional[str]] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    historias: Mapped[list["HistoriaClinica"]] = relationship(
        back_populates="paciente", cascade="all, delete-orphan"
    )
    citas: Mapped[list["Cita"]] = relationship(
        back_populates="paciente", cascade="all, delete-orphan"
    )


# ─── HISTORIA CLÍNICA ─────────────────────────────────────────────────────────

class HistoriaClinica(Base):
    __tablename__ = "historias_clinicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    motivo_consulta: Mapped[str] = mapped_column(Text, nullable=False)
    anamnesis: Mapped[Optional[str]] = mapped_column(Text)
    examen_fisico: Mapped[Optional[str]] = mapped_column(Text)
    diagnostico: Mapped[Optional[str]] = mapped_column(Text)
    tratamiento: Mapped[Optional[str]] = mapped_column(Text)
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    paciente: Mapped["Paciente"] = relationship(back_populates="historias")
    cita_id: Mapped[Optional[int]] = mapped_column(ForeignKey("citas.id"))


# ─── CITA ─────────────────────────────────────────────────────────────────────

class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id"), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duracion_minutos: Mapped[int] = mapped_column(Integer, default=30)
    motivo: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[EstadoCita] = mapped_column(
        SAEnum(EstadoCita), default=EstadoCita.agendada
    )
    notas: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    paciente: Mapped["Paciente"] = relationship(back_populates="citas")


# ─── CONTABILIDAD ─────────────────────────────────────────────────────────────

class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[TipoMovimiento] = mapped_column(SAEnum(TipoMovimiento), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(10), default="#6B7280")

    movimientos: Mapped[list["Movimiento"]] = relationship(back_populates="categoria")


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[TipoMovimiento] = mapped_column(SAEnum(TipoMovimiento), nullable=False)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    moneda: Mapped[Moneda] = mapped_column(SAEnum(Moneda), default=Moneda.pyg)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    cita_id: Mapped[Optional[int]] = mapped_column(ForeignKey("citas.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    categoria: Mapped[Optional["Categoria"]] = relationship(back_populates="movimientos")
