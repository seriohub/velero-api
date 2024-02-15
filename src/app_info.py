from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import app_info

from utils.app_data import __version__, __app_name__, __app_description__, __app_summary__
from libs.config import ConfigEnv

config = ConfigEnv()

# docs and redoc
docs_url = '/docs'
re_docs_url = '/redoc'
enabled_docs = config.get_api_disable_documentation()
if not enabled_docs:
    docs_url = None
    re_docs_url = None

# info api with allow origins from *
appInfo = FastAPI(
    title=__app_name__,
    description=__app_description__,
    summary=__app_summary__,
    version=__version__,
    license_info={
        'name': 'Apache 2.0',
        'identifier': 'Apache-2.0',
    },
    docs_url=docs_url,
    redoc_url=re_docs_url,
)

appInfo.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

appInfo.include_router(app_info.router)
