import fastapi.middleware.cors as _cors

from typing import Union
from fastapi import FastAPI

app = FastAPI()

'''
Configuração de CORS

origins = [
    "http://127.0.0.1:8080",

]

app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

'''
@app.get("/")
def read_root():
    return {"oi": "oi"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}