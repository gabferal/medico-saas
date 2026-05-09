"""
Script de inicialización con datos de demostración.
Ejecutar con: python seed.py
"""
import sys
import os
import random
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.models import (
    Usuario, Paciente, HistoriaClinica, Cita,
    Categoria, Movimiento,
    TipoDocumento, EstadoCita, TipoMovimiento, Moneda
)
from app.core.config import get_settings

settings = get_settings()

NOMBRES = [
    "María García López", "Juan Carlos Rodríguez", "Ana Beatriz Martínez",
    "Pedro Antonio López", "Carmen Rosa Silva", "Luis Alberto Fernández",
    "Rosa Elena Benítez", "Carlos Ernesto Núñez", "Elena Patricia Gómez",
    "Miguel Ángel Torres", "Lucía Ramírez Duarte", "José González Insfrán",
    "Sofía Cardozo Acosta", "Diego Giménez Pereira", "Valentina Romero Cruz",
    "Francisco Escobar Vera", "Claudia Vásquez Monge", "Roberto Álvarez Ríos",
    "Patricia Mendoza Soto", "Alejandro Cabrera Lima",
]

CIUDADES_PY = [
    "Pedro Juan Caballero", "Concepción", "Amambay", "Bella Vista Norte",
]
CIUDADES_BR = ["Ponta Porã", "Dourados", "Campo Grande"]

MOTIVOS = [
    "Control de rutina", "Dolor de cabeza persistente", "Fiebre y malestar general",
    "Hipertensión arterial", "Diabetes — control", "Dolor abdominal",
    "Infección respiratoria", "Revisión de exámenes", "Embarazo — primer control",
    "Seguimiento post-quirúrgico",
]

DIAGNOSTICOS = [
    "Hipertensión arterial leve — estadio I", "Diabetes mellitus tipo 2 controlada",
    "Resfriado común", "Gastritis crónica", "Anemia ferropénica leve",
    "Faringitis aguda", "Embarazo 12 semanas — evolución normal", "Sin novedad patológica",
    "Bronquitis aguda", "Lumbalgia mecánica",
]

TRATAMIENTOS = [
    "Enalapril 5 mg/día, control en 30 días", "Metformina 500 mg c/12h, dieta sin azúcar",
    "Reposo, paracetamol 500 mg c/8h, hidratación", "Omeprazol 20 mg/día en ayunas",
    "Sulfato ferroso 300 mg/día, vitamina C", "Azitromicina 500 mg/día × 3 días",
    "Control obstétrico mensual, ácido fólico 5 mg", "Control en 6 meses",
    "Amoxicilina 875 mg c/12h × 7 días", "Ibuprofeno 400 mg c/8h, fisioterapia",
]


def seed():
    db = SessionLocal()
    try:
        print("🌱 Iniciando carga de datos de demostración...")

        # ── Usuario médico ────────────────────────────────────────────────────
        if not db.query(Usuario).filter(Usuario.email == settings.admin_email).first():
            db.add(Usuario(
                email=settings.admin_email,
                nombre="Dr. Carlos Augusto Mendoza",
                password_hash=hash_password(settings.admin_password),
            ))
            db.flush()
            print(f"   ✅ Usuario creado: {settings.admin_email}")
        else:
            print(f"   ℹ️  Usuario ya existe: {settings.admin_email}")

        # ── Categorías contables ──────────────────────────────────────────────
        categorias_data = [
            ("Consulta médica", "ingreso", "#10B981"),
            ("Procedimiento médico", "ingreso", "#3B82F6"),
            ("Laboratorio y análisis", "ingreso", "#8B5CF6"),
            ("Certificado médico", "ingreso", "#F59E0B"),
            ("Alquiler del consultorio", "gasto", "#EF4444"),
            ("Insumos médicos", "gasto", "#F97316"),
            ("Servicios públicos", "gasto", "#6B7280"),
            ("Equipamiento", "gasto", "#EC4899"),
            ("Capacitación / Cursos", "gasto", "#06B6D4"),
        ]
        cats_por_nombre = {}
        for nombre, tipo, color in categorias_data:
            existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
            if not existe:
                c = Categoria(nombre=nombre, tipo=TipoMovimiento(tipo), color=color)
                db.add(c)
                db.flush()
                cats_por_nombre[nombre] = c.id
            else:
                cats_por_nombre[nombre] = existe.id
        print(f"   ✅ {len(categorias_data)} categorías configuradas")

        # ── Pacientes ─────────────────────────────────────────────────────────
        pacientes_existentes = db.query(Paciente).count()
        pacientes_nuevos = []
        if pacientes_existentes == 0:
            for i, nombre in enumerate(NOMBRES):
                es_brasil = i >= 16  # últimos 4 son brasileños
                ciudad = random.choice(CIUDADES_BR if es_brasil else CIUDADES_PY)
                pais = "Brasil" if es_brasil else "Paraguay"
                tipo_doc = TipoDocumento.cpf_br if es_brasil else TipoDocumento.cedula_py

                p = Paciente(
                    nombre_completo=nombre,
                    tipo_documento=tipo_doc,
                    numero_documento=(
                        f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
                        if es_brasil
                        else str(random.randint(1_000_000, 9_999_999))
                    ),
                    fecha_nacimiento=date(
                        random.randint(1950, 2010),
                        random.randint(1, 12),
                        random.randint(1, 28),
                    ),
                    sexo=random.choice(["Masculino", "Femenino"]),
                    telefono=f"09{random.randint(71,99)}-{random.randint(100000, 999999)}",
                    correo=f"{nombre.split()[0].lower()}{random.randint(1,999)}@gmail.com",
                    ciudad=ciudad,
                    pais=pais,
                    creado_en=datetime.utcnow() - timedelta(days=random.randint(0, 300)),
                )
                db.add(p)
                db.flush()
                pacientes_nuevos.append(p)

                # Historia clínica (1-3 registros por paciente)
                for _ in range(random.randint(1, 3)):
                    idx = random.randint(0, len(MOTIVOS) - 1)
                    db.add(HistoriaClinica(
                        paciente_id=p.id,
                        fecha=date.today() - timedelta(days=random.randint(1, 200)),
                        motivo_consulta=MOTIVOS[idx % len(MOTIVOS)],
                        diagnostico=DIAGNOSTICOS[idx % len(DIAGNOSTICOS)],
                        tratamiento=TRATAMIENTOS[idx % len(TRATAMIENTOS)],
                        observaciones="Paciente colaborador, sin alergias conocidas.",
                    ))

            print(f"   ✅ {len(pacientes_nuevos)} pacientes creados con historia clínica")
        else:
            print(f"   ℹ️  Ya existen {pacientes_existentes} pacientes")
            pacientes_nuevos = db.query(Paciente).all()

        # ── Citas ─────────────────────────────────────────────────────────────
        if db.query(Cita).count() == 0:
            estados = list(EstadoCita)
            for i in range(25):
                p = random.choice(pacientes_nuevos)
                dias_offset = random.randint(-10, 20)
                hora = random.randint(8, 17)
                fh = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=dias_offset, hours=hora - datetime.now().hour)
                estado = EstadoCita.realizada if dias_offset < -1 else (
                    EstadoCita.agendada if dias_offset > 0 else random.choice(estados)
                )
                db.add(Cita(
                    paciente_id=p.id,
                    fecha_hora=fh,
                    duracion_minutos=random.choice([20, 30, 45, 60]),
                    motivo=random.choice(MOTIVOS),
                    estado=estado,
                ))
            print("   ✅ 25 citas creadas")

        # ── Movimientos financieros (90 días) ─────────────────────────────────
        if db.query(Movimiento).count() == 0:
            cats_ingreso = [n for n, t, _ in categorias_data if t == "ingreso"]
            cats_gasto = [n for n, t, _ in categorias_data if t == "gasto"]

            for dia_offset in range(90, -1, -1):
                fecha_mov = date.today() - timedelta(days=dia_offset)
                # Consultas diarias (2-6)
                for _ in range(random.randint(2, 6)):
                    cat_nombre = random.choice(cats_ingreso)
                    db.add(Movimiento(
                        tipo=TipoMovimiento.ingreso,
                        categoria_id=cats_por_nombre.get(cat_nombre),
                        descripcion=cat_nombre,
                        monto=random.choice([100_000, 150_000, 200_000, 250_000, 300_000, 350_000]),
                        moneda=Moneda.pyg,
                        fecha=fecha_mov,
                    ))

                # Gastos (1-2 por semana)
                if random.random() < 0.25:
                    cat_nombre = random.choice(cats_gasto)
                    db.add(Movimiento(
                        tipo=TipoMovimiento.gasto,
                        categoria_id=cats_por_nombre.get(cat_nombre),
                        descripcion=cat_nombre,
                        monto=random.choice([30_000, 50_000, 80_000, 120_000, 200_000, 1_500_000]),
                        moneda=Moneda.pyg,
                        fecha=fecha_mov,
                    ))

            print("   ✅ Movimientos financieros de 90 días creados")

        db.commit()
        print()
        print("═" * 50)
        print("✅ Datos de demostración cargados correctamente.")
        print(f"   🔑 Correo:      {settings.admin_email}")
        print(f"   🔑 Contraseña:  {settings.admin_password}")
        print("═" * 50)

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
