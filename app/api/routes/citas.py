from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Cita, Paciente
from app.schemas.schemas import CitaCreate, CitaUpdate, CitaOut

router = APIRouter(prefix="/citas", tags=["Citas"])


def _enriquecer(cita: Cita) -> dict:
    d = {c.key: getattr(cita, c.key) for c in cita.__table__.columns}
    d["paciente_nombre"] = cita.paciente.nombre_completo if cita.paciente else None
    return d


@router.get("", response_model=list[CitaOut])
def listar_citas(
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    paciente_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Cita).options(joinedload(Cita.paciente))
    if desde:
        q = q.filter(Cita.fecha_hora >= datetime.combine(desde, datetime.min.time()))
    if hasta:
        q = q.filter(Cita.fecha_hora <= datetime.combine(hasta, datetime.max.time()))
    if paciente_id:
        q = q.filter(Cita.paciente_id == paciente_id)
    citas = q.order_by(Cita.fecha_hora).all()
    return [_enriquecer(c) for c in citas]


@router.post("", response_model=CitaOut, status_code=201)
def crear_cita(
    data: CitaCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if not db.query(Paciente).filter(Paciente.id == data.paciente_id).first():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    cita = Cita(**data.model_dump())
    db.add(cita)
    db.commit()
    db.refresh(cita)
    db.expire(cita)
    cita = db.query(Cita).options(joinedload(Cita.paciente)).filter(Cita.id == cita.id).first()
    return _enriquecer(cita)


@router.get("/{cita_id}", response_model=CitaOut)
def obtener_cita(
    cita_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cita = db.query(Cita).options(joinedload(Cita.paciente)).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return _enriquecer(cita)


@router.put("/{cita_id}", response_model=CitaOut)
def actualizar_cita(
    cita_id: int,
    data: CitaUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cita = db.query(Cita).options(joinedload(Cita.paciente)).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cita, k, v)
    db.commit()
    db.refresh(cita)
    cita = db.query(Cita).options(joinedload(Cita.paciente)).filter(Cita.id == cita_id).first()
    return _enriquecer(cita)


@router.delete("/{cita_id}", status_code=204)
def cancelar_cita(
    cita_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    db.delete(cita)
    db.commit()
