from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from datetime import datetime, date
from typing import Optional
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/usuario")
def crear_usuario(data: schemas.UsuarioCreateRequest, db: Session = Depends(get_db)):
    
    existe = db.query(models.Usuario)\
        .filter(models.Usuario.username == data.username)\
        .first()
    
    if existe:
        return {"success": False, "message": "El nombre de usuario ya existe"}
    
    usuario = models.Usuario(
        username=data.username,
        email=data.email,
        pin_hash=data.pin
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {"success": True, "id_usuario": usuario.id}


@app.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):

    usuario = db.query(models.Usuario)\
        .filter(models.Usuario.username == data.username)\
        .first()

    if not usuario:
        return {"success": False}

    if usuario.pin_hash != data.pin:
        return {"success": False}

    return {
        "success": True,
        "id_usuario": usuario.id
    }



from datetime import date

@app.post("/movimiento")
def crear_movimiento(data: schemas.MovimientoRequest, db: Session = Depends(get_db)):
    try:
        fecha_db = db.query(models.Fecha).filter_by(fecha=data.fecha).first()

        if not fecha_db:
            fecha_db = models.Fecha(
                fecha=data.fecha,
                anio=data.fecha.year,
                mes=data.fecha.month,
                nombre_mes=data.fecha.strftime("%B"),
                dia=data.fecha.day,
                dia_semana=data.fecha.strftime("%A"),
                es_fin_de_semana=1 if data.fecha.weekday() >= 5 else 0
            )
            db.add(fecha_db)
            db.flush()

        mov = models.Movimiento(
            id_usuario=data.id_usuario,
            id_cuenta=data.id_cuenta,
            id_categoria=data.id_categoria,
            id_fecha=fecha_db.id_fecha,
            monto=data.monto,
            descripcion=data.descripcion
        )

        db.add(mov)
        db.commit()

        return {"message": "Movimiento registrado correctamente"}

    except Exception as e:
        db.rollback()
        raise e



@app.get("/resumen/{id_usuario}")
def resumen(id_usuario: int, db: Session = Depends(get_db)):

    movimientos = db.query(models.Movimiento)\
        .filter(models.Movimiento.id_usuario == id_usuario)\
        .all()

    total = sum(m.monto for m in movimientos)

    return {
        "total_movimientos": len(movimientos),
        "total": total
    }


@app.get("/movimientos/{id_usuario}")
def obtener_movimientos(id_usuario: int, db: Session = Depends(get_db)):

    movimientos = db.query(models.Movimiento)\
        .filter(models.Movimiento.id_usuario == id_usuario)\
        .all()

    return {
        "movimientos": [
            {
                "monto": m.monto,
                "descripcion": m.descripcion,
                "id_categoria": m.id_categoria,
                "id_cuenta": m.id_cuenta,
                "id_fecha": m.id_fecha
            }
            for m in movimientos
        ]
    }




@app.get("/presupuesto/{id_usuario}/{id_fecha}")
def obtener_presupuesto(id_usuario: int, id_fecha: int, db: Session = Depends(get_db)):

    presupuestos = db.query(models.Presupuesto)\
        .filter(
            models.Presupuesto.id_usuario == id_usuario,
            models.Presupuesto.id_fecha == id_fecha
        ).all()

    return {
        "presupuesto": [
            {
                "id_categoria": p.id_categoria,
                "monto": p.monto
            }
            for p in presupuestos
        ]
    }


