from os.path import isfile, isdir
from os import mkdir

from sqlalchemy import create_engine

from models import (
    metadata_obj,
    MainTable,
    VUZTable,
    ProgTable,
    RegionTable,
    DistTable,
    MinistryTable,
)

def create_tables():
    if not(isdir('DB')):
        mkdir('DB')
    engine = create_engine("sqlite:///DB/DataBase.sqlite", echo=False)
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    main_table = MainTable()
    vuz_table = VUZTable()
    prog_table = ProgTable()
    reg_table = RegionTable()
    dist_table = DistTable()
    minis_table = MinistryTable()
    main_table.create_table()
    vuz_table.create_table()
    prog_table.create_table()
    reg_table.create_table()
    dist_table.create_table()
    minis_table.create_table()

