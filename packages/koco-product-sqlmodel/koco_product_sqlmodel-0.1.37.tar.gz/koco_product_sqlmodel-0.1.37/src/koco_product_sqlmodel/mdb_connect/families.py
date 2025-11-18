from sqlmodel import Session, select
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.dbmodels.definition as sql_def
import koco_product_sqlmodel.fastapi.routes.spectable as mdb_c
import koco_product_sqlmodel.fastapi.routes.article as mdb_a


def create_family(family: sql_def.CFamily) -> sql_def.CFamily:
    if not family:
        return
    with Session(mdb_con.mdb_engine) as session:
        session.add(family)
        session.commit()
        statement = (
            select(sql_def.CFamily)
            .where(sql_def.CFamily.family == family.family)
            .where(sql_def.CFamily.product_group_id == family.product_group_id)
        )
        return session.exec(statement=statement).one_or_none()


def create_family_DB(family: sql_def.CFamilyPost) -> sql_def.CFamily:
    if not family:
        return
    with Session(mdb_con.mdb_engine) as session:
        session.add(family)
        session.commit()
        statement = (
            select(sql_def.CFamily)
            .where(sql_def.CFamily.family == family.family)
            .where(sql_def.CFamily.product_group_id == family.product_group_id)
        )
        return session.exec(statement=statement).one_or_none()


def update_family_DB(
    id: int | None, fam_post: sql_def.CFamilyPost
) -> sql_def.CFamily | None:
    if id == None:
        return
    with Session(mdb_con.mdb_engine) as session:
        statement = select(sql_def.CFamily).where(sql_def.CFamily.id == id)
        fam = session.exec(statement=statement).one_or_none()
        if fam == None:
            return
        fam_data = fam_post.model_dump(exclude_unset=True)
        fam = fam.sqlmodel_update(fam_data)
        session.add(fam)
        session.commit()
        session.refresh(fam)
    return fam


def get_families_db(product_group_id: int = None) -> list[sql_def.CFamily]:
    if not product_group_id:
        statement = select(sql_def.CFamily)
    else:
        statement = select(sql_def.CFamily).where(
            sql_def.CFamily.product_group_id == product_group_id
        )
    with Session(mdb_con.mdb_engine) as session:
        return session.exec(statement=statement).all()


def get_family_db_by_id(
    id: int, include_siblings: bool = False
) -> sql_def.CFamily | sql_def.CFamilyFullGet | None:
    statement = select(sql_def.CFamily).where(sql_def.CFamily.id == id)
    if not include_siblings:
        with Session(mdb_con.mdb_engine) as session:
            return session.exec(statement=statement).one_or_none()
    with Session(mdb_con.mdb_engine) as session:
        family = session.exec(statement=statement).one_or_none()
        if not family:
            return None
        full_family = sql_def.CFamilyFullGet(**family.model_dump())
        statement = select(sql_def.CApplication).where(
            sql_def.CApplication.family_id == family.id
        )
        full_family.applications = session.exec(statement=statement).all()
        full_family.articles = mdb_a.ArticleRoute(
            sqlmodel_db=sql_def.CArticle,
            sqlmodel_post=sql_def.CArticlePost,
            sqlmodel_get=sql_def.CArticleFullGet,
            tags=[],
        ).get_objects(family_id=family.id, include_siblings=True)
        statement = select(sql_def.COption).where(
            sql_def.COption.family_id == family.id
        )
        full_family.options = session.exec(statement=statement).all()
        full_family.spectables = mdb_c.SpecTableRoute(
            sqlmodel_db=sql_def.CSpecTable,
            sqlmodel_post=sql_def.CSpecTablePost,
            sqlmodel_get=sql_def.CSpecTableFullGet,
            tags=[],
        ).get_objects(parent_id=family.id, parent="family", include_siblings=True)
        return full_family


def main() -> None:
    pass


if __name__ == "__main__":
    main()
