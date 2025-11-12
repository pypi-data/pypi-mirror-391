from enum import IntEnum
from urllib.parse import quote_plus

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class EstadoMonitoreo(IntEnum):
    CORRECTO = 0
    FINALIZADO_CON_ERRORES = 1
    ERRONEO = 2


ESTADO_MEANINGS = {
    EstadoMonitoreo.CORRECTO: "Correcto",
    EstadoMonitoreo.FINALIZADO_CON_ERRORES: "Proceso finalizado con errores",
    EstadoMonitoreo.ERRONEO: "Erróneo",
}


class MonitoreoBots(Base):
    __tablename__ = "monitoreo_bots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    proceso = Column(Text)
    estado = Column(Integer)  # 0, 1, 2
    iniciado = Column(DateTime)
    finalizado = Column(DateTime)
    cliente = Column(String(50), nullable=True)
    items_count = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)  # Text maps to NVARCHAR(MAX) in SQL Server when using pyodbc


class SqlServerClient:
    def __init__(self, user: str, password: str, host: str, dbname: str, driver: str) -> None:
        driver = quote_plus(driver)
        self.connection_string = f"mssql+pyodbc://{user}:{password}@{host}/{dbname}?driver={driver}"
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def insertar_monitoreo(self, **kwargs: object) -> MonitoreoBots | None:
        required_fields = ["username", "proceso", "estado", "iniciado", "finalizado"]
        # cliente, items_count y observaciones son opcionales
        missing_fields = [field for field in required_fields if field not in kwargs]
        if missing_fields:
            raise TypeError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validar estado
        estado = kwargs["estado"]
        if isinstance(estado, EstadoMonitoreo):
            kwargs["estado"] = ESTADO_MEANINGS[estado]
        elif isinstance(estado, int):
            if estado not in [e.value for e in EstadoMonitoreo]:
                raise ValueError(f"estado debe ser uno de {[e.value for e in EstadoMonitoreo]}")
        else:
            raise TypeError("estado debe ser un int o EstadoMonitoreo")

        session = self.Session()
        try:
            nuevo_registro = MonitoreoBots(**kwargs)
            session.add(nuevo_registro)
            session.commit()
            session.refresh(nuevo_registro)
            return nuevo_registro
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()


if __name__ == "__main__":
    import os
    from datetime import datetime

    from dotenv import load_dotenv

    load_dotenv()
    user_env = os.getenv("DB_USER", "")
    password_env = os.getenv("DB_PASSWORD", "")
    host_env = os.getenv("DB_HOST", "")
    dbname_env = os.getenv("DB_NAME", "")
    driver_env = os.getenv("DB_DRIVER", "")
    cliente_db = SqlServerClient(user_env, password_env, host_env, dbname_env, driver_env)
    registro = cliente_db.insertar_monitoreo(
        username="lmarinaro",
        proceso="Scraping semanal",
        estado=EstadoMonitoreo.CORRECTO,
        iniciado=datetime(2025, 9, 25, 10, 0),
        finalizado=datetime(2025, 9, 25, 10, 15),
        cliente="BPS",
        items_count=42,
    )
