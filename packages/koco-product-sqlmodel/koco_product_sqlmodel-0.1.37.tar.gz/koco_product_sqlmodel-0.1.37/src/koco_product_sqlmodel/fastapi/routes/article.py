from fastapi import HTTPException, Request

import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.mdb_connect.mdb_connector as mdb_con
import koco_product_sqlmodel.fastapi.routes.generic_route as rgen
import koco_product_sqlmodel.fastapi.routes.security as rsec
from koco_product_sqlmodel.mdb_connect.import_excel import log_changes
from koco_product_sqlmodel.fastapi.routes.spectable import SpecTableRoute


class ArticleRoute(rgen.MyBaseRoute):
    def __init__(
        self,
        sqlmodel_db: sqlm.SQLModel,
        sqlmodel_post: sqlm.SQLModel,
        sqlmodel_get: sqlm.SQLModel,
        tags: list[str],
    ):
        super().__init__(
            sqlmodel_db=sqlmodel_db,
            sqlmodel_post=sqlmodel_post,
            sqlmodel_get=sqlmodel_get,
            tags=tags,
        )

    async def post_object(
        self, object: sqlm.CArticlePost, request: Request
    ) -> sqlm.SQLModel:
        object.user_id = await rsec.get_user_id_from_request(request=request)
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return await self.get_and_log_updated_model(
            request=request, updated_object=new_obj
        )

    async def patch_object(
        self, id: int, obj: sqlm.CArticlePost, request: Request
    ) -> sqlm.SQLModel:
        obj.user_id = await rsec.get_user_id_from_request(request=request)
        updated_object = mdb_gen.patch_object(
            id=id, db_obj=obj, db_obj_type=self.sqlmodel_db
        )
        if updated_object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return await self.get_and_log_updated_model(
            request=request, updated_object=updated_object
        )

    async def delete_object(
        self, id: int, delete_recursive: bool = True, request: Request = None
    ) -> dict[str, bool]:
        """
        Delete an article item by carticle.id.

        * Request parameter: *delete_recursive* = true

        If set to *true* all subitems contained in given article will be removed from database to avoid orphaned data
        """
        user_id = await rsec.get_user_id_from_request(request=request)
        mdb_con.delete_article_by_id(
            article_id=id,
            delete_connected_items=delete_recursive,
            user_id=user_id,
            log_func=log_changes,
        )
        return {"ok": True}

    def get_objects(
        self, family_id: int = None, include_siblings: bool = False
    ) -> list[sqlm.CArticleFullGet]:
        """
        GET list of objects from DB.
        Optional parameter:
        * *family_id* - when specified, only objects from the selected family are retrieved
        """
        objects = mdb_gen.get_family_related_objects(
            db_obj_type=self.sqlmodel_db, family_id=family_id
        )
        objects_get: list[sqlm.SQLModel] = []
        if not include_siblings:
            for object in objects:
                objects_get.append(self.sqlmodel_get(**object.model_dump()))
            return objects_get
        for object in objects:
            r_model = sqlm.CArticleFullGet(**object.model_dump())
            r_model.spectables = SpecTableRoute(
                sqlmodel_db=sqlm.CSpecTable,
                sqlmodel_post=sqlm.CSpecTablePost,
                sqlmodel_get=sqlm.CSpecTableFullGet,
                tags=[],
            ).get_objects(parent_id=object.id, parent="article", include_siblings=True)
            objects_get.append(r_model)
        return objects_get

    def get_object(self, id, include_siblings: bool = False) -> sqlm.SQLModel:
        object = mdb_gen.get_object(db_obj_type=self.sqlmodel_db, id=id)
        if object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        if not include_siblings:
            return sqlm.CArticleGet(**object.model_dump())
        r_model = sqlm.CArticleFullGet(**object.model_dump())
        r_model.spectables = SpecTableRoute(
            sqlmodel_db=sqlm.CSpecTable,
            sqlmodel_post=sqlm.CSpecTablePost,
            sqlmodel_get=sqlm.CSpecTableFullGet,
            tags=[],
        ).get_objects(parent_id=object.id, parent="article", include_siblings=True)
        return r_model


route_article = ArticleRoute(
    sqlmodel_db=sqlm.CArticle,
    sqlmodel_get=sqlm.CArticleFullGet,
    sqlmodel_post=sqlm.CArticlePost,
    tags=["Endpoints to ARTICLE-data"],
)


def main():
    pass


if __name__ == "__main__":
    main()
