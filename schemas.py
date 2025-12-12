from pydantic import BaseModel

class LoginRequest(BaseModel):
    pin: str

class MovimientoRequest(BaseModel):
    tipo: str
    categoria: str
    monto: float
    fecha: str
