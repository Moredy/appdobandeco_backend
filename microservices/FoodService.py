from warnings import catch_warnings
from firebase_admin import db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DefaultResponseModel(BaseModel):
    statusCode: int
    message:str


@router.put(
    "/foodService/givefoodlike/{food_id}/{user_id}",
    response_model=DefaultResponseModel
)
def give_food_like(food_id: int, user_id: str):
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
       return {"statusCode": 500, "message": "Este usuário ja deu like nessa comida."}

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

    return {"statusCode": 200, "message": "Like adicionado com sucesso."}


@router.put(
    "/foodService/removefoodlike/{food_id}/{user_id}",
    response_model=DefaultResponseModel
)
def remove_food_like(food_id: int, user_id: str):
    userRef = db.reference( 'users/').child(user_id);
    userLikesRef = db.reference( 'users/' + user_id+ '/' +likedFoods)
    foodRef = db.reference( 'foods/'+ str(food_id));

    likedFoods = []
    totalFoodLikes = 0

    try:
        likedFoods = userRef.get()['likedFoods']
    except:
        return {"statusCode": 500, "message": "Este usuário nunca deu like em nenhuma comida."}

    #Caso não tenha dado like na comida
    if likedFoods.__contains__(food_id): 
        likedFoods.remove(food_id)
    else:
       return {"statusCode": 500, "message": "Esse usuário não deu like nessa comida."}


    if likedFoods == []:
        userLikesRef.remove()
    else:
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

    return {"statusCode": 200, "message": "Like descontado com sucesso."}


