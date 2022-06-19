import fastapi.middleware.cors as _cors
import firebase_admin
from typing import Union
from fastapi import FastAPI
from microservices import FoodService
from microservices import MenuService
from microservices import ReportService
from microservices import UserService
from fastapi.responses import RedirectResponse

databaseURL = 'https://appdobandeco-default-rtdb.firebaseio.com';

cred_obj = firebase_admin.credentials.Certificate('./firebase_credentials.json')
firebase_admin.initialize_app(cred_obj, {'databaseURL': databaseURL})

app = FastAPI()

'''
Configuração de CORS
'''
origins = ["*"]

app.add_middleware(
    _cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(FoodService.router)
app.include_router(MenuService.router)
app.include_router(ReportService.router)
app.include_router(UserService.router)

@app.get("/")
def read_root():
    return RedirectResponse("/redoc")
