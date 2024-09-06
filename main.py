from fastapi import FastAPI, Depends, HTTPException
from app.routes import router
from app.models import engine
from config import Config
from elasticsearch import Elasticsearch
import asyncio

app = FastAPI()

MAPPING_FOR_INDEX = {
            "properties": {
                "iD": {
                    "type": "long",
                },
                "text": {
                    "type": "text"
                }
            },
        }

async def create_index():
    es = Elasticsearch([Config.ELASTICSEARCH_URL])
    es.indices.create(index="documents", mappings=MAPPING_FOR_INDEX, ignore=400)

app.include_router(router)

if __name__ == "__main__":
    asyncio.run(create_index())
    uvicorn.run(app, port=8000, host='0.0.0.0')