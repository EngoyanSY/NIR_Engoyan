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
        data = pd.read_excel(os.path.join("DB", self._schema.table_name))
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

class MainTable(BaseTabel):
    _schema = Py_Main
    __table__ = Table(
        "main",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("idlistedu", Integer),
        Column("idparent", Integer),
        Column("progid", Integer),
        Column("fieldid", String),
        Column("profile", String),
        Column("course1", Integer),
        Column("course2", String),
        Column("course3", String),
        Column("course4", String),
        Column("course5", String),
        Column("course6", String),
        Column("course7", String),
    )

class VUZTable(BaseTabel):
    _schema = Py_VUZ
    __table__ = Table(
        "vuz",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("idlistedu", Integer),
        Column("idparent", Integer),
        Column("fullname", Integer),
        Column("name", String),
        Column("adress", String),
        Column("rector", Integer),
        Column("id_region", String),
        Column("id_district", String),
        Column("id_ministry", String),
    )

class ProgTable(BaseTabel):
    _schema = Py_VUZ
    __table__ = Table(
        "programms",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("progid", Integer),
        Column("progname", Integer),
        Column("progcode", Integer),
    )

class TrainTable(BaseTabel):
    _schema = Py_Trainings
    __table__ = Table(
        "trainings",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("fieldif", Integer),
        Column("fieldname", Integer),
        Column("progid", Integer),
        Column("progcode", Integer),
    )

class RegionTable(BaseTabel):
    _schema = Py_Regions
    __table__ = Table(
        "trainings",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_region", Integer),
        Column("region", Integer),
        Column("id_district", Integer),
    )

class DistTable(BaseTabel):
    _schema = Py_Districts
    __table__ = Table(
        "districts",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_district", Integer),
        Column("district", Integer),
    )

class DistTable(BaseTabel):
    _schema = Py_Districts
    __table__ = Table(
        "districts",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_ministry", Integer),
        Column("ministry", Integer),
    )

