from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import HistoriaClinica, Paciente
from app.schemas.schemas import HistoriaCreate, HistoriaUpdate, HistoriaOut

router = APIRouter(prefix="/historias", tags=["Historia Clínica"])


@router.get("/paciente/{paciente_id}", response_model=list[HistoriaOut])
def historias_de_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return (
        db.query(HistoriaClinica)
        .filter(HistoriaClinica.paciente_id == paciente_id)
        .order_by(HistoriaClinica.fecha.desc())
        .all()
    )


@router.post("", response_model=HistoriaOut, status_code=201)
def crear_historia(
    data: HistoriaCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # Verificar que el paciente existe
    if not db.query(Paciente).filter(Paciente.id == data.paciente_id).first():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    historia = HistoriaClinica(**data.model_dump())
    db.add(historia)
    db.commit()
    db.refresh(historia)
    return historia


@router.get("/{historia_id}", response_model=HistoriaOut)
def obtener_historia(
    historia_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    h = db.query(HistoriaClinica).filter(HistoriaClinica.id == historia_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    return h


@router.put("/{historia_id}", response_model=HistoriaOut)
def actualizar_historia(
    historia_id: int,
    data: HistoriaUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    h = db.query(HistoriaClinica).filter(HistoriaClinica.id == historia_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(h, k, v)
    db.commit()
    db.refresh(h)
    return h


@router.delete("/{historia_id}", status_code=204)
def eliminar_historia(
    historia_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    h = db.query(HistoriaClinica).filter(HistoriaClinica.id == historia_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    db.delete(h)
    db.commit()
