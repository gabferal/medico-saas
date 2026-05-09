from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional
import csv, io
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Movimiento, Categoria, TipoMovimiento
from app.schemas.schemas import MovimientoCreate, MovimientoOut, CategoriaCreate, CategoriaOut

router = APIRouter(prefix="/contabilidad", tags=["Contabilidad"])


# ─── Categorías ───────────────────────────────────────────────────────────────

@router.get("/categorias", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Categoria).order_by(Categoria.nombre).all()


@router.post("/categorias", response_model=CategoriaOut, status_code=201)
def crear_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cat = Categoria(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categorias/{cat_id}", status_code=204)
def eliminar_categoria(
    cat_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cat = db.query(Categoria).filter(Categoria.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(cat)
    db.commit()


# ─── Movimientos ──────────────────────────────────────────────────────────────

@router.get("/movimientos", response_model=list[MovimientoOut])
def listar_movimientos(
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    tipo: Optional[TipoMovimiento] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Movimiento)
    if desde:
        q = q.filter(Movimiento.fecha >= desde)
    if hasta:
        q = q.filter(Movimiento.fecha <= hasta)
    if tipo:
        q = q.filter(Movimiento.tipo == tipo)
    return q.order_by(Movimiento.fecha.desc()).offset(skip).limit(limit).all()


@router.post("/movimientos", response_model=MovimientoOut, status_code=201)
def crear_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    mov = Movimiento(**data.model_dump())
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.delete("/movimientos/{mov_id}", status_code=204)
def eliminar_movimiento(
    mov_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    mov = db.query(Movimiento).filter(Movimiento.id == mov_id).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(mov)
    db.commit()


# ─── Resumen / Flujo de caja ──────────────────────────────────────────────────

@router.get("/resumen")
def resumen_flujo(
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Movimiento)
    if desde:
        q = q.filter(Movimiento.fecha >= desde)
    if hasta:
        q = q.filter(Movimiento.fecha <= hasta)

    movimientos = q.all()
    ingresos = sum(m.monto for m in movimientos if m.tipo == TipoMovimiento.ingreso)
    gastos = sum(m.monto for m in movimientos if m.tipo == TipoMovimiento.gasto)

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "saldo": ingresos - gastos,
        "cantidad_movimientos": len(movimientos),
    }


# ─── Exportar CSV ─────────────────────────────────────────────────────────────

@router.get("/exportar/csv")
def exportar_csv(
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Movimiento)
    if desde:
        q = q.filter(Movimiento.fecha >= desde)
    if hasta:
        q = q.filter(Movimiento.fecha <= hasta)
    movimientos = q.order_by(Movimiento.fecha).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Tipo", "Categoría", "Descripción", "Monto", "Moneda"])
    for m in movimientos:
        writer.writerow([
            m.fecha,
            "Ingreso" if m.tipo == TipoMovimiento.ingreso else "Gasto",
            m.categoria.nombre if m.categoria else "",
            m.descripcion,
            m.monto,
            m.moneda,
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flujo_caja.csv"},
    )
