from elasticsearch import Elasticsearch

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Document, SessionLocal
from config import Config

app = FastAPI()
router = APIRouter()
app.include_router(router)



es = Elasticsearch([Config.ELASTICSEARCH_URL])

def create_index():
    mapping = {
        "properties": {
            "text": {"type": "text"},
            "id": {"type": "integer"}
        }
    }
    es.indices.create(index='documents', body=mapping, ignore=400)





def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create_document")
async def create_document(
        document: dict,
        db: Session = Depends(get_db),
):
    db_doc = Document(**document)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    text = db_doc.text
    id = db_doc.id

    es.index(index='documents', body={'text': text, 'id': id})

    return {"message": "Document created successfully"}

@router.get("/search")
async def search(q: str = None, db: Session = Depends(get_db)):
    if q is None:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    search_results = es.search(index='documents', body={
        "query": {
            "match": {
                "text": q
            }
        },
        "sort": [
            {"id.keyword": {"order": "asc", "unmapped_type": "long"}}
        ],
        "size": 20
    })

    results = search_results['hits']['hits']
    ids = [hit['_source']['id'] for hit in results]

    documents = db.query(Document).filter(Document.id.in_(ids)).all()

    return [{
        'id': doc.id,
        'rubrics': doc.rubrics,
        'text': doc.text,
        'created_date': doc.created_date.isoformat()
    } for doc in documents]


@router.delete("/delete_document")
async def delete_document(id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()

    es.delete_by_query(index='documents', query={"match": {"iD": id}})
    es.indices.refresh(index='documents')

    return {"message": "Document deleted successfully"}