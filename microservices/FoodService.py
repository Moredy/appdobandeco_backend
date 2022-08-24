from array import array
from multiprocessing.dummy import Array
from warnings import catch_warnings
from firebase_admin import db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
import json
from fastapi.encoders import jsonable_encoder
from microservices.MenuService import get_menu_by_date_and_type
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


#Get Total Nutrients By Date Type
@router.get("/foodService/getTotalNutrientsByDateType/{date}/{vegan}/{dinner}", response_model=GetResponseModel)
async def get_total_nutrients_by_date_type(date, vegan, dinner, request: Request, response: Response):
    try:
        customPrefStr = request.query_params['customPrefStr']
        customPrefObj = json.loads(customPrefStr)
    except:
        customPrefObj = {}

    print('customPrefObj')
    print(customPrefObj)
    totalCalories = 0
    totalProteins = 0
    totalLipids = 0
    totalCarbohydrates = 0

    menu = await get_menu_by_date_and_type(date ,vegan, dinner, response)
    menu = menu['dataObj']['menuArray']

    allFoods = await get_all_foods_data(response)
    allFoods = allFoods['dataObj']['foodsArray']

    for food_id in menu:
        for foodObj in allFoods:
            #print(foodObj['id'])
            if foodObj['id'] == food_id:
                try:
                    if foodObj['portion'] > 0:

                        customFoodObj = customPrefObj['foods'][food_id]

                        totalProteins += (float(customFoodObj['portion'])*foodObj['proteins'])/foodObj['portion']
                        totalCalories += (float(customFoodObj['portion'])*foodObj['calories'])/foodObj['portion']
                        totalLipids +=(float(customFoodObj['portion'])*foodObj['lipids'])/foodObj['portion']
                        totalCarbohydrates += (float(customFoodObj['portion'])*foodObj['carbohydrates'])/foodObj['portion']
                    else:
                        raise ZeroDivisionError;
                except:
                    totalProteins += foodObj['proteins']
                    totalCalories += foodObj['calories']
                    totalLipids += foodObj['lipids']
                    totalCarbohydrates += foodObj['carbohydrates']



    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {"calories" : round(totalCalories,2), "proteins" : round(totalProteins,2), "lipids" : round(totalLipids,2), "carbohydrates": round(totalCarbohydrates,2)}};


#Get Total Nutrients By Date Type And Nutrient
@router.get("/foodService/getTotalNutrientsByDateTypeNutrient/{date}/{vegan}/{nutrient}", response_model=GetResponseModel)
async def get_total_nutrients_by_date_type_nutrient(date, vegan, nutrient, response: Response):
    total = 0

    menu = await get_menu_by_date_and_type(date ,vegan , response)
    menu = menu['dataObj']['menuArray']

    allFoods = await get_all_foods_data(response)
    allFoods = allFoods['dataObj']['foodsArray']

    for food_id in menu:
        for foodObj in allFoods:
            print(foodObj['id'])
            if foodObj['id'] == food_id:
                total += foodObj[nutrient]



    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {"total" : total}};


#Get food by id
@router.get("/foodService/getFoodById/{food_id}", response_model=GetResponseModel)
async def get_food_by_id(food_id, response: Response):
    foodRef = db.reference( 'foods/');
    foodData = foodRef.child(food_id).get()

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": foodData};

#Get food by name and desc
@router.get("/foodService/getFoodIdByNameAndDesc/{name}/{desc}", response_model=GetResponseModel)
async def get_Food_Id_By_Name_Desc(name, desc, response: Response):
    foodRef = db.reference( 'foods/');
    foodData = foodRef.get()

    foodId = ''

    for food in foodData:
        foodObjRef = foodRef.child(food)
        foodObj = foodObjRef.get()
        if foodObj['foodName'] == name and foodObj['foodDesc'] == desc:
            foodId = foodObjRef.key

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": {"foodId" : foodId}};




#Get all foods
@router.get("/foodService/getAllFoodsData/", response_model=GetResponseModel)
async def get_all_foods_data(response: Response):
    foodRef = db.reference( 'foods/');
    foodData = foodRef.get()

    foodData_array = []

    for item in foodData:
        food = foodRef.child(item);
        foodObj = food.get()
        foodData_array.append({
            "id": food.key,
            "foodName": foodObj['foodName'],
            "foodType": foodObj['foodType'],
            "foodShortDesc": foodObj['foodShortDesc'],
            "foodDesc" : foodObj['foodDesc'],
            "proteins": foodObj['proteins'],
            "portion": foodObj['portion'],
            "foodImage" : foodObj['foodImage'],
            "carbohydrates" : foodObj['carbohydrates'],
            "lipids": foodObj['lipids'],
            "calories": foodObj['calories']
        })

    Dict = {"foodsArray": foodData_array}

    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "dataObj": Dict};




#Create Food - POST
class FoodBody(BaseModel):
    foodName: str
    foodType: str
    foodShortDesc: str
    foodDesc : str
    proteins: int
    porcao: int
    #spoonSizeInGrams: int
    foodImage : str
    carbohydrates : int
    lipids: int
    likes: int
    calories: int

@router.post("/foodService/createFood/", response_model=CreateResponseModel)
async def create_food(foodBody: FoodBody, response: Response):
    foodRef = db.reference( 'foods/');
    json_compatible_item_data = jsonable_encoder(foodBody)
    #print(json_compatible_item_data)
    newFoodRef = foodRef.push(json_compatible_item_data);

    response.status_code = status.HTTP_201_CREATED
    return {"statusCode": response.status_code, "uid": newFoodRef.key};




#Give like to a food - PUT
@router.put(
    "/foodService/givefoodlike/{food_id}/{user_id}",
    response_model=DefaultResponseModel
)
def give_food_like(food_id: str, user_id: str , response: Response):
    userRef = db.reference( 'users/').child(user_id);
    foodRef = db.reference( 'foods/'+ str(food_id));

    likedFoods = []
    totalFoodLikes = 0

    try:
        likedFoods = userRef.get()['likedFoods']
    except:
        print("--Esse usuário ainda não deu like em nenhuma comida, adicionando primeiro registro")


    #Caso não tenha dado like na comida
    if not likedFoods.__contains__(food_id):
        likedFoods.append(food_id)
    else:
       response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR;
       return {"statusCode": response.status_code, "message": "Este usuário ja deu like nessa comida."}

    userRef.update({
        'likedFoods' : likedFoods
    })

    #Adiciona o like na comida
    try:
        totalFoodLikes = foodRef.get()['likes'];
    except:
        print("Essa comida ainda não recebeu likes, adicionando primeiro registro")

    totalFoodLikes += 1;

    foodRef.update({
        'likes' : totalFoodLikes
    })
    response.status_code = status.HTTP_200_OK
    return {"statusCode": response.status_code, "message": "Like adicionado com sucesso."}


#Remove like of food - PUT
@router.put(
    "/foodService/removefoodlike/{food_id}/{user_id}",
    response_model=DefaultResponseModel
)
def remove_food_like(food_id: str, user_id: str, response: Response):
    userRef = db.reference( 'users/').child(user_id);
    foodRef = db.reference( 'foods/'+ str(food_id));

    likedFoods = []
    totalFoodLikes = 0

    try:
        likedFoods = userRef.get()['likedFoods']
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR;
        return {"statusCode": response.status_code, "message": "Este usuário nunca deu like em nenhuma comida."}

    #Caso não tenha dado like na comida
    if likedFoods.__contains__(food_id):
        likedFoods.remove(food_id)
    else:
       response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR;
       return {"statusCode": response.status_code, "message": "Esse usuário não deu like nessa comida."}


    userRef.update({
        'likedFoods' : likedFoods
    })

    #Adiciona o like na comida
    try:
        totalFoodLikes = foodRef.get()['likes'];
    except:
        print("Essa comida ainda não recebeu likes, adicionando primeiro registro")

    totalFoodLikes -= 1;

    foodRef.update({
        'likes' : totalFoodLikes
    })

    response.status_code = status.HTTP_200_OK;
    return {"statusCode": response.status_code, "message": "Like descontado com sucesso."}


