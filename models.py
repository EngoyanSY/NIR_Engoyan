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
)
from sqlalchemy.orm import DeclarativeBase
from core import Session
import pandas as pd

from schema import (
    Py_Main,
    Py_VUZ,
    Py_Programms,
    Py_Trainings,
    Py_Regions,
    Py_Districts,
    Py_Ministries,
    Py_InfoVUZ,
)


def create_sql_tables():
    if not (os.path.isdir("DB")):
        os.mkdir("DB")
    if not (os.path.isfile("DB/DataBase.sqlite")):
        engine = create_engine("sqlite:///DB/DataBase.sqlite", echo=False)
        metadata_obj.drop_all(engine)
        metadata_obj.create_all(engine)
        print("База данных инициализирована")

        main_table = MainTable()
        vuz_table = VUZTable()
        prog_table = ProgTable()
        train_table = TrainTable()
        reg_table = RegionTable()
        dist_table = DistTable()
        minis_table = MinistriesTable()
        info_table = InfoVUZ()

        info_table.create_table()
        main_table.create_table()
        vuz_table.create_table()
        prog_table.create_table()
        train_table.create_table()
        reg_table.create_table()
        dist_table.create_table()
        minis_table.create_table()

        print("База данных создана")


metadata_obj = MetaData()


class BaseTabel(DeclarativeBase):
    _schema = BaseModel

    def create_table(self):
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


class MinistriesTable(BaseTabel):
    _schema = Py_Ministries
    __table__ = Table(
        "ministries",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("id_ministry", Integer),
        Column("ministry", String),
    )


def create_info_vuz():
    vuz = VUZTable().__table__.c
    reg = RegionTable().__table__.c
    dist = DistTable().__table__.c
    minis = MinistriesTable().__table__.c
    info = InfoVUZ().__table__
    with Session() as session:
        results = (
            session.query(
                vuz.UniqueID,
                vuz.name,
                vuz.adress,
                reg.region,
                dist.district,
                minis.ministry,
            )
            .join(reg, reg.id_region == vuz.id_region)
            .join(dist, dist.id_district == vuz.id_district)
            .join(minis, minis.id_ministry == vuz.id_ministry)
            .all()
        )

        insert_stmt = info.insert().values(
            [
                {
                    "UniqueID": row[0],
                    "vuzname": row[1],
                    "adress": row[2],
                    "region": row[3],
                    "district": row[4],
                    "ministry": row[5],
                }
                for row in results
            ]
        )

        session.execute(insert_stmt)
        session.commit()


class InfoVUZ(BaseTabel):
    _schema = Py_InfoVUZ
    __table__ = Table(
        "vuz_info",
        metadata_obj,
        Column("UniqueID", Integer, primary_key=True),
        Column("vuzname", String),
        Column("adress", String),
        Column("region", String),
        Column("district", String),
        Column("ministry", String),
    )


def get_vuz_info(filter = 0):
    #1 - Главные
    #2 - Филлиалы
    #0/ничего - по порядку все
    with Session() as sess:
        query = (
            select(VUZTable.idlistedu, VUZTable.idparent, VUZTable.name)
            .join(RegionTable, VUZTable.id_region == RegionTable.id_region)
            .join(DistTable, VUZTable.id_district == DistTable.id_district)
            .join(MinistriesTable, VUZTable.id_ministry == MinistriesTable.id_ministry)
        )

        
        if filter == 1:
            query = query.where(VUZTable.idlistedu == VUZTable.idparent)
        elif filter == 2:
            query = query.where(VUZTable.idlistedu != VUZTable.idparent)
        res = sess.execute(query).all()
        return len(res)


def get_train_info(vuz = False, prog = False, formname = False):
    #vuz - list(idlistedu, idparent)
    #prog - 62 - б, 65 - с, 68 - м
    #form - 1 - очная, 2 - заочная, 3 - очно-заочная
    form = {
        1 : "очная", 
        2 : "заочная", 
        3 : "очно-заочная", 
    }
    with Session() as sess:
        query = (
            select(
                TrainTable.fieldid,
                TrainTable.fieldname,
                ProgTable.progname,
                MainTable.formname,
                MainTable.course1,
                MainTable.course2,
                MainTable.course3,
                MainTable.course4,
                MainTable.course5,
                MainTable.course6,
                MainTable.course7,
            )
            .join(ProgTable, ProgTable.progid == MainTable.progid)
            .join(TrainTable, TrainTable.fieldid == MainTable.fieldid)
        )
        if prog:
            query = query.where(MainTable.progid == prog)
        if vuz:
            query = (query
                     .where(MainTable.idlistedu == vuz[0])
                     .where(MainTable.idparent == vuz[1])
            )
        if formname:
            query = query.where(MainTable.formname == form.get(formname))
            
        res = sess.execute(query).all()
        return res