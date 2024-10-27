import os
import numpy as np

from pydantic import BaseModel
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    create_engine,
    insert,
    select,
    func,
    union_all,
    literal_column,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
import pandas as pd

from schema import (
    Py_Main,
    Py_VUZ,
    Py_Programms,
    Py_Trainings,
    Py_Regions,
    Py_Districts,
    Py_Ministry,
)

metadata_obj = MetaData()

class BaseTabel(DeclarativeBase):
    _schema = BaseModel

    def create_table(self):
        # Считывает xlsx файл
        # Переименовывает столбцы и заменяет отсуттвующие данные на None
        # Построчно валидирует данные через Pydantic и вносит их в таблицу
        data = pd.read_excel(os.path.join("data", self._schema.table_name))
        data = data.rename(
            columns=dict(zip(data.columns, list(self._schema.model_fields)))
        )
        data.replace({np.nan: None}, inplace=True)
        engine = create_engine("sqlite:///DB/DataBase.sqlite", echo=False)
        with Session(engine) as session:
            for r in range(data.shape[0]):
                table_model = self._schema.model_validate(data.iloc[r].to_dict())
                stmt = insert(self.__table__).values(table_model.dict())
                session.execute(stmt)
            session.commit()
            session.close()
        print(f"Таблица {self.__table__} создана")

class MainTable(BaseTabel):
    _schema = Py_Main
    __table__ = Table(
        "main",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("idlistedu", Integer),
        Column("idparent", Integer),
        Column("progid", Integer),
        Column("fieldid", Integer),
        Column("profile", String),
        Column("formname", String),
        Column("course1", Integer),
        Column("course2", Integer),
        Column("course3", Integer),
        Column("course4", Integer),
        Column("course5", Integer),
        Column("course6", Integer),
        Column("course7", Integer),
    )

class VUZTable(BaseTabel):
    _schema = Py_VUZ
    __table__ = Table(
        "vuz",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("idlistedu", Integer),
        Column("idparent", Integer),
        Column("fullname", String),
        Column("name", String),
        Column("adress", String),
        Column("rector", String),
        Column("id_region", Integer),
        Column("id_district", Integer),
        Column("id_ministry", Integer),
    )

class ProgTable(BaseTabel):
    _schema = Py_Programms
    __table__ = Table(
        "programms",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("progid", Integer),
        Column("progname", String),
        Column("progcode", Integer),
    )

class TrainTable(BaseTabel):
    _schema = Py_Trainings
    __table__ = Table(
        "trainings",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("fieldid", String),
        Column("fieldname", String),
        Column("progid", Integer),
        Column("progcode", Integer),
    )

class RegionTable(BaseTabel):
    _schema = Py_Regions
    __table__ = Table(
        "regions",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_region", Integer),
        Column("region", String),
        Column("id_district", Integer),
    )

class DistTable(BaseTabel):
    _schema = Py_Districts
    __table__ = Table(
        "districts",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_district", Integer),
        Column("district", String),
    )

class MinistryTable(BaseTabel):
    _schema = Py_Ministry
    __table__ = Table(
        "ministry",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_ministry", Integer),
        Column("ministry", String),
    )

