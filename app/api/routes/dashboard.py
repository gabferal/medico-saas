from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Paciente, Cita, Movimiento, TipoMovimiento, EstadoCita

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
def obtener_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    # Totales
    total_pacientes = db.query(Paciente).filter(Paciente.activo == True).count()
    pacientes_este_mes = db.query(Paciente).filter(
        Paciente.activo == True,
        Paciente.creado_en >= datetime.combine(inicio_mes, datetime.min.time()),
    ).count()

    # Citas de hoy
    citas_hoy = db.query(Cita).filter(
        func.date(Cita.fecha_hora) == hoy,
        Cita.estado != EstadoCita.cancelada,
    ).count()

    # Ingresos del mes
    ingresos_mes = db.query(func.sum(Movimiento.monto)).filter(
        Movimiento.tipo == TipoMovimiento.ingreso,
        Movimiento.fecha >= inicio_mes,
    ).scalar() or 0

    # Consultas por mes (últimos 6 meses)
    consultas_por_mes = (
        db.query(
            extract("year", Cita.fecha_hora).label("anio"),
            extract("month", Cita.fecha_hora).label("mes"),
            func.count(Cita.id).label("total"),
        )
        .filter(
            Cita.estado == EstadoCita.realizada,
            Cita.fecha_hora >= datetime(hoy.year - 1 if hoy.month <= 6 else hoy.year, 
                                        (hoy.month - 6) % 12 or 12, 1),
        )
        .group_by("anio", "mes")
        .order_by("anio", "mes")
        .all()
    )

    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    consultas_data = [
        {"mes": f"{meses_es[int(r.mes)-1]} {int(r.anio)}", "consultas": r.total}
        for r in consultas_por_mes
    ]

    # Distribución por edad
    pacientes = db.query(Paciente.fecha_nacimiento).filter(
        Paciente.activo == True,
        Paciente.fecha_nacimiento != None,
    ).all()

    dist_edad = {"0-17": 0, "18-35": 0, "36-59": 0, "60+": 0}
    for (fnac,) in pacientes:
        edad = (hoy - fnac).days // 365
        if edad < 18:
            dist_edad["0-17"] += 1
        elif edad < 36:
            dist_edad["18-35"] += 1
        elif edad < 60:
            dist_edad["36-59"] += 1
        else:
            dist_edad["60+"] += 1

    return {
        "total_pacientes": total_pacientes,
        "pacientes_este_mes": pacientes_este_mes,
        "citas_hoy": citas_hoy,
        "ingresos_mes": float(ingresos_mes),
        "consultas_por_mes": consultas_data,
        "distribucion_edad": dist_edad,
    }
