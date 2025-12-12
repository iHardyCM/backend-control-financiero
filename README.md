******Backend FastAPI (Control Financiero)******
Este backend provee los servicios REST que usa la aplicación móvil Control Financiero, desarrollado con FASTAPI, SQLite y SQLAlchemy.

********************************************************************************
****Características principales****

**API REST con FASTAPI**
provee endpoints para:
- Login por PIN
- Registrar movimientos (gastos/ingresos)
- Obtener resumen financier (ingresos, gastos, saldo)
- Obtener presupuesto

**Base de datos con SQLite**
Usa SQLAlchemy para gestionar modelos
- Usuarios
- Movimientos

**Relación 1 -> N**
Un usuario puede tener múltiples movimientos.

********************************************************************************
**Tecnologías utilizadas**
- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic (schemas)

********************************************************************************
**Intalación y ejecución**
- Clonar el repositorio: git clone <URL_DEL_BACKEND>
- Instalar dependencias: pip install -r requeriments.txt
- Ejecutar el servidor FastAPI: uvicorn main:app --reload
- El backend se expone en: http://127.0.0.1:8000
- Y la documentación Swagger en: http://127.0.0.1:8000/docs

********************************************************************************
****Modelo de Base de datos****
**Usuario**

| Campo | Tipo     | Descripción     |
| ----- | -------- | --------------- |
| id    | int (PK) | Identificador   |
| pin   | int      | PIN del usuario |

**Movimientos**

| Campo      | Tipo     | Descripción                |
| ---------- | -------- | -------------------------- |
| id         | int (PK) | Identificador              |
| tipo       | string   | "Gasto" o "Ingreso"        |
| categoria  | string   | Categoría (solo en Gastos) |
| monto      | float    | Monto del movimiento       |
| fecha      | string   | Fecha (dd/mm/yyyy)         |
| usuario_id | int      | FK → Usuarios.id           |

********************************************************************************
******Endpoints******

****Login****
**POST/Login**
Body:
{
  "pin": 1234
}

Respuesta:
{
  "success": true
}

****Registrar movimientos****
**POST/movimiento**
Body
{
  "tipo": "Gasto",
  "categoria": "Hogar",
  "monto": 250.0,
  "fecha": "09/12/2024"
}

****Registrar movimientos****
**GET/resumen**
Devuelve (ejemplo):
{
  "ingresos": 3500.0,
  "gastos": 900.0,
  "disponible": 2600.0,
  "movimientos": [
      {"categoria": "Hogar", "monto": 250},
      {"categoria": "Alimentos", "monto": 150},
  ]
}

****Obtener presupuesto****
**GET/presupuesto**
Ejemplo:
{
  "alimentos": 200,
  "transporte": 150,
  "servicios": 300
}




