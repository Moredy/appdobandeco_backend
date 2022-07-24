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
    message: str


class CreateResponseModel(BaseModel):
    statusCode: int
    uid: str


class GetResponseModel(BaseModel):
    statusCode: int
    dataObj: dict




@router.get("/rankingService/getRanking/{foodType}", response_model=GetResponseModel)
async def get_ranking(foodType, response: Response):

    rankingListFinal = []

    foodRef = db.reference( 'foods/');

    rankingList = foodRef.get()

    foodsInFoodType = []

    for itemKey in rankingList:
        #print(rankingList[itemKey])
        if rankingList[itemKey]['foodType'] == foodType:
            foodsInFoodType.append({'key': itemKey , 'obj': rankingList[itemKey]})

    foodsInFoodType.sort(key=lambda x: x['obj']['likes'])

    for food in foodsInFoodType:
        rankingListFinal.append(food['key'])

    rankingListFinal.reverse()

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {"rankingArray": rankingListFinal}};
