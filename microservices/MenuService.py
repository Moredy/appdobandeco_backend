from array import array
from multiprocessing.dummy import Array
from warnings import catch_warnings
from firebase_admin import db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

router = APIRouter()


class DefaultResponseModel(BaseModel):
    statusCode: int
    message:str

class CreateResponseModel(BaseModel):
    statusCode: int
    uid:str

class GetResponseModel(BaseModel):
    statusCode: int
    dataObj: dict

#Create Menu

class MenuBody(BaseModel):
    vegan: list
    notVegan: list
    dinnerVegan: list
    dinnerNotVegan: list

@router.post("/menuService/createMenu/{dateStr}", response_model=DefaultResponseModel)
async def create_menu(dateStr, menuBody: MenuBody, response: Response):
    menuRef = db.reference( 'menus/'+ dateStr);
    json_compatible_item_data = jsonable_encoder(menuBody)
    menuRef.update(json_compatible_item_data);

    response.status_code = status.HTTP_201_CREATED
    return {"statusCode": response.status_code, "message": "Menu criado com sucesso, para acessa-lo utilize a data"};



#Get all menus Data
@router.get("/menuService/getAllMenusData/", response_model=GetResponseModel)
async def get_all_menus_data(response: Response):
    menuRef = db.reference( 'menus/');
    menuData = menuRef.get()

    menuDict = {}
    
    for item in menuData:
        menu = menuRef.child(item);
        menuObj = menu.get()
        menuDict[item] = {
            "vegan": menuObj['vegan'],
            "notVegan": menuObj['notVegan'],
        }


    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": menuDict};


#Get menu by date and type
@router.get("/menuService/getMenuByDateAndType/{date}/{vegan}/{dinner}", response_model=GetResponseModel)
async def get_menu_by_date_and_type(date , vegan , dinner, response: Response):
    menuRef = db.reference( 'menus/').child(date);
    menuData = menuRef.get()

    if dinner == False:
        menuList = menuData[vegan]

    if dinner == True and vegan == 'vegan':
        menuList = menuData['dinnerVegan']

    if dinner == False and vegan == 'notVegan':
        menuList = menuData['dinnerNotVegan']


    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {"menuArray": menuList}};


