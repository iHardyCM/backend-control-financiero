from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from datetime import datetime, date, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Security
import hashlib
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/backoffice", StaticFiles(directory="backoffice"), name="backoffice")
SECRET_KEY = "control-financiero-backoffice-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = int(expire.timestamp())  # 👈 CLAVE
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()

def verify_pin(pin: str, hashed: str) -> bool:
    return hashlib.sha256(pin.encode("utf-8")).hexdigest() == hashed

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def require_admin(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="No autorizado")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")



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
        pin_hash=hash_pin(data.pin)

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

    if usuario.estado != "ACTIVO":
        return {"success": False, "message": "Usuario bloqueado"}
    
    if not verify_pin(data.pin, usuario.pin_hash):
        return {"success": False}

    return {
        "success": True,
        "id_usuario": usuario.id
    }


@app.post("/admin/login")
def admin_login(data: schemas.LoginRequest, db: Session = Depends(get_db)):

    user = db.query(models.Usuario)\
        .filter(models.Usuario.username == data.username)\
        .first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if user.estado != "ACTIVO":
        raise HTTPException(status_code=403, detail="Usuario bloqueado")

    # Regla rápida de ADMIN (simple y efectiva)
    if user.username != "admin":
        raise HTTPException(status_code=403, detail="No es administrador")

    if not verify_pin(data.pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_token({
        "sub": str(user.id),
        "role": "ADMIN"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }



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
        db.refresh(mov)

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


# @app.get("/movimientos/{id_usuario}")
# def obtener_movimientos(id_usuario: int, db: Session = Depends(get_db)):

#     movimientos = db.query(models.Movimiento)\
#         .filter(models.Movimiento.id_usuario == id_usuario)\
#         .all()

#     return {
#         "movimientos": [
#             {
#                 "monto": m.monto,
#                 "descripcion": m.descripcion,
#                 "id_categoria": m.id_categoria,
#                 "id_cuenta": m.id_cuenta,
#                 "id_fecha": m.id_fecha
#             }
#             for m in movimientos
#         ]
#     }


@app.get("/movimientos_mes/{id_usuario}")
def obtener_movimientos_mes(id_usuario: int, db: Session = Depends(get_db)):

    hoy = date.today()

    movimientos = (
        db.query(models.Movimiento)
        .join(models.Fecha, models.Movimiento.id_fecha == models.Fecha.id_fecha)
        .filter(
            models.Movimiento.id_usuario == id_usuario,
            models.Fecha.anio == hoy.year,
            models.Fecha.mes == hoy.month
        )
        .all()
    )

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


@app.post("/presupuesto")
def guardar_presupuesto(data: schemas.PresupuestoRequest, db: Session = Depends(get_db)):

    # eliminar presupuesto previo del mismo mes/categoría
    db.query(models.Presupuesto).filter(
        models.Presupuesto.id_usuario == data.id_usuario,
        models.Presupuesto.id_categoria == data.id_categoria,
        models.Presupuesto.id_fecha == data.id_fecha
    ).delete()

    nuevo = models.Presupuesto(
        id_usuario=data.id_usuario,
        id_categoria=data.id_categoria,
        id_fecha=data.id_fecha,
        monto=data.monto
    )

    db.add(nuevo)
    db.commit()

    return {"success": True}


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


@app.get("/movimientos/{id_usuario}")
def obtener_movimientos(id_usuario: int, db: Session = Depends(get_db)):

    movimientos = (
        db.query(
            models.Movimiento.monto,
            models.Movimiento.id_categoria,
            models.Movimiento.id_cuenta,
            models.Fecha.anio,
            models.Fecha.mes
        )
        .join(models.Fecha, models.Movimiento.id_fecha == models.Fecha.id_fecha)
        .filter(models.Movimiento.id_usuario == id_usuario)
        .all()
    )

    return {
        "movimientos": [
            {
                "monto": m.monto,
                "id_categoria": m.id_categoria,
                "id_cuenta": m.id_cuenta,
                "yyyymm": m.anio * 100 + m.mes
            }
            for m in movimientos
        ]
    }


@app.get("/admin/usuarios", response_model=list[schemas.UsuarioAdminResponse])
def admin_listar_usuarios(db: Session = Depends(get_db)):
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.estado != "ELIMINADO")
        .all()
    )


@app.get("/admin/usuarios/{id}", response_model=schemas.UsuarioAdminResponse)
def admin_obtener_usuario(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not user:
        return {"error": "Usuario no encontrado"}
    return user


@app.patch("/admin/usuarios/{id}/estado")
def admin_cambiar_estado(id: int, estado: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()

    if not user:
        return {"success": False, "message": "Usuario no encontrado"}

    user.estado = estado
    db.commit()

    return {"success": True, "estado": estado}


@app.post("/admin/usuarios/{id}/reset_pin")
def admin_reset_pin(id: int, nuevo_pin: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=404)

    user.pin_hash = hash_pin(nuevo_pin)
    db.commit()
    return {"success": True}


@app.delete("/admin/usuarios/{id}", dependencies=[Depends(require_admin)])
def admin_eliminar_usuario(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.username == "admin":
        raise HTTPException(status_code=400, detail="No se puede eliminar admin")

    user.estado = "ELIMINADO"
    db.commit()

    return {"success": True}


@app.put("/admin/usuarios/{id}", dependencies=[Depends(require_admin)])
def admin_editar_usuario(
    id: int,
    data: schemas.UsuarioUpdateRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.email = data.email
    db.commit()

    return {"success": True, "email": data.email}





@app.get("/admin/usuarios/{id}/resumen")
def admin_resumen_usuario(id: int, db: Session = Depends(get_db)):
    total_mov = db.query(models.Movimiento)\
        .filter(models.Movimiento.id_usuario == id)\
        .count()

    total_gastos = db.query(models.Movimiento.monto)\
        .join(models.Categoria, models.Movimiento.id_categoria == models.Categoria.id_categoria)\
        .filter(
            models.Movimiento.id_usuario == id,
            models.Categoria.tipo == "GASTO"
        ).all()

    return {
        "total_movimientos": total_mov,
        "total_gastos": sum(m[0] for m in total_gastos)
    }


@app.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    total = db.query(models.Usuario)\
        .filter(models.Usuario.estado != "ELIMINADO")\
        .count()

    activos = db.query(models.Usuario)\
        .filter(models.Usuario.estado == "ACTIVO")\
        .count()

    bloqueados = db.query(models.Usuario)\
        .filter(models.Usuario.estado == "BLOQUEADO")\
        .count()

    return {
        "total_usuarios": total,
        "usuarios_activos": activos,
        "usuarios_bloqueados": bloqueados
    }

