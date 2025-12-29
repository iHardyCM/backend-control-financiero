from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine

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

    if usuario and usuario.pin_hash == data.pin:
        return {"success": True, "id_usuario": usuario.id}

    return {"success": False}




@app.post("/movimiento")
def crear_movimiento(data: schemas.MovimientoRequest, db: Session = Depends(get_db)):

    if not db.query(models.Cuenta).filter_by(id_cuenta=data.id_cuenta).first():
        return {"error": "Cuenta no válida"}

    if not db.query(models.Categoria).filter_by(id_categoria=data.id_categoria).first():
        return {"error": "Categoría no válida"}

    mov = models.Movimiento(
        id_usuario=data.id_usuario,
        id_cuenta=data.id_cuenta,
        id_categoria=data.id_categoria,
        id_fecha=data.id_fecha,
        monto=data.monto,
        descripcion=data.descripcion
    )
    db.add(mov)
    db.commit()
    return {"message": "Movimiento registrado"}





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


