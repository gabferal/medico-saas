from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Paciente
from app.schemas.schemas import PacienteCreate, PacienteUpdate, PacienteOut, PacienteResumen
from typing import Optional

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("", response_model=list[PacienteResumen])
def listar_pacientes(
    buscar: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Paciente).filter(Paciente.activo == True)
    if buscar:
        q = q.filter(
            or_(
                Paciente.nombre_completo.ilike(f"%{buscar}%"),
                Paciente.numero_documento.ilike(f"%{buscar}%"),
            )
        )
    return q.order_by(Paciente.nombre_completo).offset(skip).limit(limit).all()


@router.post("", response_model=PacienteOut, status_code=201)
def crear_paciente(
    data: PacienteCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    paciente = Paciente(**data.model_dump())
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


@router.get("/{paciente_id}", response_model=PacienteOut)
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return p


@router.put("/{paciente_id}", response_model=PacienteOut)
def actualizar_paciente(
    paciente_id: int,
    data: PacienteUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{paciente_id}", status_code=204)
def eliminar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    p.activo = False  # Soft delete
    db.commit()
