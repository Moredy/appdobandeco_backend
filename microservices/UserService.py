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



@router.get("/userService/getAllUsersData/", response_model=GetResponseModel)
async def get_all_users_data(response: Response):
    usersRef = db.reference( 'users/');
    usersData = usersRef.get()
    usersData_array = []
    
    for item in usersData:
        users = usersRef.child(item);
        usersObj = users.get()
        usersData_array.append({
            "user_uid": users.key,
            "email": usersObj['email'],
            "likedFoods": usersObj['likedFoods'],
            "name": usersObj['name'],
            "photoURL" : usersObj['photoURL'],
            "providerId": usersObj['providerId'],
            "unicampAccount": usersObj['unicampAccount'],
        })

    Dict = {"reportsArray": usersData_array}

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": Dict};

    #Get food by id
@router.get("/userService/getUserByUid/{user_uid}", response_model=GetResponseModel)
async def get_user_by_uid(user_uid, response: Response):
    usersRef = db.reference( 'users/');
    usersData = usersRef.child(user_uid).get()

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": usersData};