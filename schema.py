from typing import Optional, ClassVar

from pydantic import BaseModel, Field, validator


class Py_Main(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    idlistedu: int = Field()
    idparent: int = Field()
    progid: int = Field()
    fieldid: str = Field()
    profile: Optional[str] = Field(default=None)
    formname: str = Field()
    course1: Optional[int] = Field(default=None)
    course2: Optional[int] = Field(default=None)
    course3: Optional[int] = Field(default=None)
    course4: Optional[int] = Field(default=None)
    course5: Optional[int] = Field(default=None)
    course6: Optional[int] = Field(default=None)
    course7: Optional[int] = Field(default=None)
    table_name: ClassVar[str] = "main.xlsx"


class Py_VUZ(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    idlistedu: int = Field()
    idparent: int = Field()
    fullname: str = Field()
    name: str = Field()
    adress: str = Field()
    rector: Optional[str] = Field(default=None)
    id_region: Optional[int] = Field()
    id_district: Optional[int] = Field()
    id_ministry: Optional[int] = Field()
    table_name: ClassVar[str] = "Вузы.xlsx"

    @validator("id_region", "id_district", "id_ministry", pre=True, always=True)
    def set_default_values(cls, v):
        return v if v is not None else 9999


class Py_Programms(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    progid: int = Field()
    progname: str = Field()
    progcode: int = Field()
    table_name: ClassVar[str] = "Программы.xlsx"


class Py_Trainings(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    fieldid: str = Field()
    fieldname: str = Field()
    progid: int = Field()
    progcode: int = Field()
    table_name: ClassVar[str] = "Направления подготовки.xlsx"


class Py_Regions(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    id_region: int = Field()
    region: str = Field()
    id_district: int = Field()
    table_name: ClassVar[str] = "Регионы.xlsx"


class Py_Districts(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    id_district: int = Field()
    district: str = Field()
    table_name: ClassVar[str] = "Округа.xlsx"


class Py_Ministry(BaseModel):
    UniqueID: Optional[int] = Field(default=None, primary_key=True, nullable=None)
    id_ministry: int = Field()
    ministry: str = Field()
    table_name: ClassVar[str] = "Министерства.xlsx"
