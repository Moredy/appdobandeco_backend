from bs4 import BeautifulSoup
from fastapi.encoders import jsonable_encoder
from lxml import etree
import requests
from firebase_admin import db
from datetime import datetime, date, time, timedelta, timezone

jobInterval = 900 #seconds
waitFirst=False



dia = str(datetime.now().date().day)
mes = str(datetime.now().date().month)
ano = str(datetime.now().date().year)

if int(dia) < 10:
  dia = '0' + dia

if int(mes) < 10:
  mes = '0' + mes


print (ano+'-'+mes+'-'+dia)
url = 'https://www.sar.unicamp.br/RU/view/site/cardapio.php?data='+ano+'-'+mes+'-'+dia

# Busca no site do SAR as comidas, adiciona as mesmas ao app caso não estejam no catalogo de comidas
# cria o menu do dia com base nos nomes das comidas



def checkIfFoodExistsByName(name):
  try:
    itensCompleted = 0
    foodRef = db.reference('foods/');
    foods = foodRef.get();
    founded = False
    len(foods)

    for key in foods:
      #print(key)
      foodObj = foods[key]
      itensCompleted += 1
      #print(itensCompleted, len(foods) )
      if foodObj['foodName'] == name:
        founded = True
    return founded
  except Exception as e:
    print('Failed: '+ str(e))
    return checkIfFoodExistsByName(name);

def addFood(name):
  foodRef = db.reference('foods/');

  foodObj = {
    "foodName": name,
    "foodType": "Não informado.",
    "foodShortDesc": "Não informado.",
    "foodDesc": "Não informado.",
    "proteins": 0,
    "portion": 0,
    "foodImage": "https://i.ibb.co/Zxbh11q/pngwing-com-1.png",
    "carbohydrates": 0,
    "lipids": 0,
    "likes": 0,
    "calories": 0
  }

  if checkIfFoodExistsByName(name) == False:
    newFoodRef = foodRef.push(foodObj);
    return newFoodRef.key
  else:
    return -1





def runJob1():
  try:
    webpage = requests.get(url, verify=False)
  except Exception as e:
    print('Failed: '+ str(e))

  soup = BeautifulSoup(webpage.content, "html.parser")
  dom = etree.HTML(str(soup))

  refeicoes = soup.find_all("table", class_="fundo_cardapio")

  menus = []


  #refeicao=refeicoes[2]

  for refeicao in refeicoes:

    try:
      pratoPrincipalElement = refeicao.find_all("strong", string="PRATO PRINCIPAL:")
      pratoPrincipal = pratoPrincipalElement[0].parent.text.split(":",1)[1].strip();


      guarnicaoElement = refeicao.find_all("strong", string="GUARNIÇÃO: ")
      guarnicao = guarnicaoElement[0].parent.text.split(":",1)[1].strip();

      proteinaElement = refeicao.find_all("strong", string="PROTEINA: ")
      proteina = proteinaElement[0].parent.text.split(":",1)[1].strip();

      saladaElement = refeicao.find_all("strong", string="SALADA: ")
      salada = saladaElement[0].parent.text.split(":",1)[1].strip();

      sobremesaElement = refeicao.find_all("strong", string="SOBREMESA: ")
      sobremesa = sobremesaElement[0].parent.text.split(":", 1)[1].strip();

      sucoElement = refeicao.find_all("strong", string="SUCO: ")
      suco = sucoElement[0].parent.text.split(":", 1)[1].strip();


      pratoPrincipal = pratoPrincipal.encode("windows-1252").decode("utf-8")
      guarnicao = guarnicao.encode("windows-1252").decode("utf-8")
      proteina = proteina.encode("windows-1252").decode("utf-8")
      salada = salada.encode("windows-1252").decode("utf-8")
      sobremesa = sobremesa.encode("windows-1252").decode("utf-8")
      suco = suco.encode("windows-1252").decode("utf-8")

      comidas = {pratoPrincipal,
                 guarnicao,
                 proteina,
                 salada,
                 sobremesa,
                 suco}

      comidas.remove('-')

      comidas.add('Arroz')
      comidas.add('Feijão')
      menus.append(comidas)

      print('''comidas''')
      for comida in comidas:
        addFood(comida)

    except Exception as e:
      menus.append({})

  almocoMenu = menus[0]
  almocoVegetarianoMenu = menus[1]
  jantarMenu = menus[2]
  jantarVegetarianoMenu = menus[3]

  def getFoodIdByName(name):
    foodRef = db.reference('foods/');
    foodData = foodRef.get()

    foodId = ''

    for food in foodData:
      #foodObjRef = foodRef.child(food)
      foodObj = foodData[food]
      if foodObj['foodName'] == name:
        foodId = food

    return foodId;

  def createMenu(menus):

    idMenus= [[],[],[],[]]

    for i, menu in enumerate(menus):
      for food in menu:
        idMenus[i].append(getFoodIdByName(food));

    menu = {
        "vegan": idMenus[0],
        "notVegan" : idMenus[1],
        "dinnerVegan" : idMenus[2],
        "dinnerNotVegan" : idMenus[3]

    }

    return menu;

  try:
    print([almocoVegetarianoMenu, almocoMenu])
    print("Aqui11")
    menuRef = db.reference('menus/' + dia+'-'+mes+'-'+ano);
    print("Aqui2")
    json_compatible_item_data = jsonable_encoder(createMenu([almocoVegetarianoMenu, almocoMenu, jantarVegetarianoMenu, jantarMenu]))
    print("Aqui3")
    menuRef.update(json_compatible_item_data);
    print("Aqui4")
  except Exception as e:
    print('Failed: '+ str(e))

  print("Success")





