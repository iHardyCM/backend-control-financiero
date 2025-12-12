from sqlalchemy import Column, Integer, String, Float
import database
Base = database.Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    pin = Column(String, unique=True, nullable=False)

class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(String)

class Presupuesto(Base):
    __tablename__ = "presupuesto"
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
