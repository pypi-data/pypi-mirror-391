from fastapi import HTTPException, Request

import koco_product_sqlmodel.fastapi.routes.security as rsec
import koco_product_sqlmodel.dbmodels.definition as sqlm
import koco_product_sqlmodel.mdb_connect.generic_object_connect as mdb_gen
import koco_product_sqlmodel.mdb_connect.categories as mdb_categories
import koco_product_sqlmodel.fastapi.routes.generic_route as rgen


class CategoryTreeRoute(rgen.MyBaseRoute):
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
        self.router.add_api_route(
            path="/{id}/families",
            endpoint=self.get_categorytree_families,
            methods=["GET"],
            response_model=list[sqlm.CFamilyGet],
        )

    def get_objects(self) -> list[sqlm.CCategoryTreeGet]:
        """
        GET list of objects from DB.
        """
        objects = mdb_gen.get_family_related_objects(
            db_obj_type=self.sqlmodel_db, family_id=None
        )
        objects_get: list[sqlm.CCategoryTreeGet] = []
        for object in objects:
            objects_get.append(self.sqlmodel_get(**object.model_dump()))
        return objects_get

    async def post_object(
        self, object: sqlm.CCategoryTreePost, request: Request
    ) -> sqlm.CCategoryTreeGet:
        object.user_id = await rsec.get_user_id_from_request(request=request)
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return await self.get_and_log_updated_model(
            request=request, updated_object=new_obj
        )

    async def patch_object(
        self, id: int, obj: sqlm.CCategoryTreePost, request: Request
    ) -> sqlm.CCategoryTreeGet:
        obj.user_id = await rsec.get_user_id_from_request(request=request)
        updated_object = mdb_gen.patch_object(
            id=id, db_obj=obj, db_obj_type=self.sqlmodel_db
        )
        if updated_object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return await self.get_and_log_updated_model(
            request=request, updated_object=updated_object
        )

    async def get_categorytree_families(
        self, id: int, request: Request
    ) -> list[sqlm.CFamilyGet]:
        """
        Get all families related to the category tree with the given ID.
        """
        objects = mdb_categories.get_families_for_category(category_id=id)
        objects_get: list[sqlm.CFamilyGet] = []
        for object in objects:
            objects_get.append(sqlm.CFamilyGet(**object.model_dump()))
        return objects_get


route_categorytree = CategoryTreeRoute(
    sqlmodel_db=sqlm.CCategoryTree,
    sqlmodel_get=sqlm.CCategoryTreeGet,
    sqlmodel_post=sqlm.CCategoryTreePost,
    tags=["Endpoints to CATEGORYTREE-data"],
)


class CategoryMapperRoute(rgen.MyBaseRoute):
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
        self, object: sqlm.CCategoryMapperPost, request: Request
    ) -> sqlm.CCategoryMapperGet:
        object.user_id = await rsec.get_user_id_from_request(request=request)
        new_obj = mdb_gen.post_object(db_obj=self.sqlmodel_db(**object.model_dump()))
        return await self.get_and_log_updated_model(
            request=request, updated_object=new_obj
        )

    async def patch_object(
        self, id: int, obj: sqlm.CCategoryMapperPost, request: Request
    ) -> sqlm.CCategoryMapperGet:
        obj.user_id = await rsec.get_user_id_from_request(request=request)
        updated_object = mdb_gen.patch_object(
            id=id, db_obj=obj, db_obj_type=self.sqlmodel_db
        )
        if updated_object == None:
            raise HTTPException(status_code=404, detail="Object not found")
        return await self.get_and_log_updated_model(
            request=request, updated_object=updated_object
        )


route_categorymapper = CategoryMapperRoute(
    sqlmodel_db=sqlm.CCategoryMapper,
    sqlmodel_get=sqlm.CCategoryMapperGet,
    sqlmodel_post=sqlm.CCategoryMapperPost,
    tags=["Endpoints to CATEGORYMAPPER-data"],
)


def main():
    pass


if __name__ == "__main__":
    main()
