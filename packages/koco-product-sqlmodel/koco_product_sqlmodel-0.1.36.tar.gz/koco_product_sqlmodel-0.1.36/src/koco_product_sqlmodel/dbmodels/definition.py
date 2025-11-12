from koco_product_sqlmodel.dbmodels.catalog import CCatalog, CCatalogGet, CCatalogPost
from koco_product_sqlmodel.dbmodels.product_group import (
    CProductGroup,
    CProductGroupGet,
    CProductGroupFullGet,
    CProductGroupPost,
)
from koco_product_sqlmodel.dbmodels.user import CUser, CUserRole
from koco_product_sqlmodel.dbmodels.family import (
    CFamily,
    CFamilyGet,
    CFamilyPost,
    CFamilyFullGet,
)
from koco_product_sqlmodel.dbmodels.article import (
    CArticle,
    CArticleGet,
    CArticleFullGet,
    CArticlePost,
)
from koco_product_sqlmodel.dbmodels.application import (
    CApplication,
    CApplicationGet,
    CApplicationPost,
)
from koco_product_sqlmodel.dbmodels.option import COption, COptionGet, COptionPost
from koco_product_sqlmodel.dbmodels.url import CUrl, CUrlGet, CUrlPost
from koco_product_sqlmodel.dbmodels.spectable import (
    CSpecTable,
    CSpecTableGet,
    CSpecTablePost,
    CSpecTableFullGet,
    CSpecTableItemParentView,
    CSpecTableItem,
    CSpecTableItemGet,
    CSpecTableItemPost,
    CSpecTableItemPatch,
    CSpecTableItemBatchDelete,
)
from koco_product_sqlmodel.dbmodels.category_tree import (
    CCategoryMapper,
    CCategoryMapperGet,
    CCategoryMapperPost,
    CCategoryTree,
    CCategoryTreeGet,
    CCategoryTreePost,
)
from koco_product_sqlmodel.dbmodels.backlog import CBacklog
from koco_product_sqlmodel.dbmodels.filedata import (
    CFileData,
    CFileDataGet,
    CFileDataPost,
)


from sqlmodel import SQLModel

# Lines needed to avoid warning due to unset inherit_cache attribute
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


def Main():
    pass


if __name__ == "__main__":
    Main()
