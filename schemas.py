from datetime import date
from pydantic import BaseModel
from typing import Optional
from typing import List


class UsuarioCreateRequest(BaseModel):
    username: str
    email: str
    pin: str


class LoginRequest(BaseModel):
    username: str
    pin: str


class MovimientoRequest(BaseModel):
    id_usuario: int
    id_cuenta: int
    id_categoria: int
    fecha: date
    monto: float
    descripcion: Optional[str] = None

class PresupuestoRequest(BaseModel):
    id_usuario: int
    id_categoria: int
    id_fecha: int
    monto: float

class ResumenResponse(BaseModel):
    id_movimiento: int
    id_cuenta: int
    id_categoria: int
    id_fecha: int
    monto: float
    descripcion: Optional[str] = None

    class Config:
        orm_mode = True

class PresupuestoResponse(BaseModel):
    id_presupuesto: int
    id_categoria: int
    id_fecha: int
    monto: float

    class Config:
        orm_mode = True

class ResumenCompletoResponse(BaseModel):
    movimientos: list[ResumenResponse]
    presupuestos: list[PresupuestoResponse]

    class Config:
        orm_mode = True

