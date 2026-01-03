from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import database

Base = database.Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String)
    pin_hash = Column(String, nullable=False)
    estado = Column(String, default="ACTIVO")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    cuentas = relationship("Cuenta", back_populates="usuario")


class Cuenta(Base):
    __tablename__ = "cuentas"

    id_cuenta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    saldo_inicial = Column(Float, default=0)
    moneda = Column(String, default="PEN")
    estado = Column(String, default="ACTIVA")

    usuario = relationship("Usuario", back_populates="cuentas")


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)

class Fecha(Base):
    __tablename__ = "fecha"

    id_fecha = Column(Integer, primary_key=True)
    fecha = Column(String)
    anio = Column(Integer)
    mes = Column(Integer)
    nombre_mes = Column(String)
    dia = Column(Integer)
    dia_semana = Column(String)
    es_fin_de_semana = Column(Integer)


class Movimiento(Base):
    __tablename__ = "movimientos"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    id_cuenta = Column(Integer, ForeignKey("cuentas.id_cuenta"))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_fecha = Column(Integer, ForeignKey("fecha.id_fecha"))

    monto = Column(Float, nullable=False)
    descripcion = Column(String)
    fecha_registro = Column(DateTime, default=datetime.utcnow)


class Presupuesto(Base):
    __tablename__ = "presupuesto"

    id_presupuesto = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    id_fecha = Column(Integer, ForeignKey("fecha.id_fecha"))
    monto = Column(Float, nullable=False)

