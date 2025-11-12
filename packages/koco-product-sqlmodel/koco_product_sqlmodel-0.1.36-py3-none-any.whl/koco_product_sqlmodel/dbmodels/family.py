from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import TIMESTAMP

from sqlmodel import Field, SQLModel, text
from sqlmodel.main import Relationship
from koco_product_sqlmodel.dbmodels.application import CApplicationGet
from koco_product_sqlmodel.dbmodels.article import CArticleFullGet
from koco_product_sqlmodel.dbmodels.option import COptionGet
from koco_product_sqlmodel.dbmodels.spectable import CSpecTableFullGet

import koco_product_sqlmodel.dbmodels.models_enums as m_enum


class CFamilyPost(SQLModel):
    family: str | None = None
    type: str | None = Field(default=None, max_length=1024)
    description: str | None = Field(default=None, max_length=4096)
    short_description: str | None = Field(default=None, max_length=1024)
    product_group_id: int | None = None
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")


class CFamilyGet(CFamilyPost):
    id: int | None = None
    upddate: datetime = None
    insdate: datetime = None


class CFamily(CFamilyGet, table=True):
    id: int | None = Field(default=None, primary_key=True)
    upddate: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        )
    )
    insdate: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    product_group_id: Optional[int] = Field(
        default=None, foreign_key="cproductgroup.id"
    )
    status: int = Field(
        default=m_enum.StatusEnum.in_work.value
    )  # general status of the data set 1: "in work", 2: "ready for review". 3: "released"
    user_id: int = Field(default=1, foreign_key="cuser.id")
    product_group: Optional["CProductGroup"] = Relationship(back_populates="families")
    articles: List["CArticle"] = Relationship(back_populates="family")
    applications: List["CApplication"] = Relationship(back_populates="family")
    options: List["COption"] = Relationship(back_populates="family")


class CFamilyFullGet(CFamilyGet):
    articles: List[CArticleFullGet] = []
    applications: List[CApplicationGet] = []
    options: List[COptionGet] = []
    spectables: List[CSpecTableFullGet] = []


def main():
    pass


if __name__ == "__main__":
    main()
