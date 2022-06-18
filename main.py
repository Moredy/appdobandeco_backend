import fastapi.middleware.cors as _cors
import firebase_admin
from typing import Union
from fastapi import FastAPI
from microservices import FoodService
from fastapi.responses import RedirectResponse

databaseURL = 'https://appdobandeco-default-rtdb.firebaseio.com';

cred_obj = firebase_admin.credentials.Certificate('./firebase_credentials.json')
firebase_admin.initialize_app(cred_obj, {'databaseURL': databaseURL})

app = FastAPI()

'''
Configuração de CORS
'''
origins = [
    "http://127.0.0.1:19002",

]

app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(FoodService.router)

@app.get("/")
def read_root():
    return RedirectResponse("/redoc")
