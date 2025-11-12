

from fastapi import APIRouter
from fastapi import Depends

from tendril.apiserver.security import security
from tendril.apiserver.security import swagger_auth


system_monitoring = APIRouter(prefix='/system',
                              tags=["System Monitoring"],
                              dependencies=[Depends(swagger_auth),
                                            security(scopes=['system:monitoring'])])

system_administration = APIRouter(prefix='/system',
                                  tags=["System Administration"],
                                  dependencies=[Depends(swagger_auth),
                                                security(scopes=['system:administration'])])


from tendril import config
from tendril.utils.versions import versions


@system_monitoring.get("/versions")
async def package_versions():
    return versions()


@system_monitoring.get("/config")
async def tendril_config():
    return config.json_render()


routers = [
    system_monitoring,
    system_administration
]
