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