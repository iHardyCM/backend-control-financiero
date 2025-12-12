from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# --- Dependencia de BD ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- LOGIN ---
@app.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.pin == data.pin).first()
    if usuario:
        return {"success": True}
    return {"success": False}


# --- REGISTRAR MOVIMIENTO ---
@app.post("/movimiento")
def crear_movimiento(data: schemas.MovimientoRequest, db: Session = Depends(get_db)):
    mov = models.Movimiento(
        tipo = data.tipo,
        categoria = data.categoria,
        monto = data.monto,
        fecha = data.fecha
    )
    db.add(mov)
    db.commit()
    return {"message": "Movimiento registrado"}


# --- RESUMEN ---
@app.get("/resumen")
def resumen(db: Session = Depends(get_db)):
    
    movimientos = db.query(models.Movimiento).all()
    total_ingresos = sum(m.monto for m in movimientos if m.tipo == "Ingreso")
    total_gastos = sum(m.monto for m in movimientos if m.tipo == "Gasto")
    disponible = total_ingresos - total_gastos

    lista_movs = [
        {"categoria": m.categoria, "monto": m.monto}
        for m in movimientos if m.tipo == "Gasto"
    ]
    
    return {
        "ingresos": total_ingresos,
        "gastos": total_gastos,
        "disponible": disponible,
        "movimientos": lista_movs
    }

@app.get("/movimientos")
def obtener_movimientos(db: Session = Depends(get_db)):
    movimientos = db.query(models.Movimiento).all()
    respuesta = []
    for m in movimientos:
        respuesta.append({
            "id": m.id,
            "tipo": m.tipo,
            "categoria": m.categoria,
            "monto": m.monto,
            "fecha": m.fecha
        })
    return {"movimientos": respuesta}


# --- PRESUPUESTO ---
@app.get("/presupuesto")
def presupuesto():
    return {
        "alimentos": 200,
        "transporte": 150,
        "servicios": 300
    }
