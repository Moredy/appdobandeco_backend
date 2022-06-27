from bs4 import BeautifulSoup
from lxml import etree
import requests
from firebase_admin import db

jobInterval = 3 #seconds
waitFirst=False

url = 'https://www.sar.unicamp.br/RU/view/site/cardapio.php?data=2022-06-14'

# Busca no site do SAR as comidas, adiciona as mesmas ao app caso não estejam no catalogo de comidas
# cria o menu do dia com base nos nomes das comidas

def checkIfFoodExistsByName(name):
  try:
    foodRef = db.reference('foods/');
    foods = foodRef.get();

    founded = False

    for key in foods:
      #print(key)
      foodObj = foodRef.child(key).get()
      if foodObj['foodName'] == name:
        founded = True

    return founded
  except:
    return False;

def addFood(name):
  foodRef = db.reference('foods/');

  foodObj = {
    "foodName": name,
    "foodType": "Não informado.",
    "foodShortDesc": "Não informado.",
    "foodDesc": "Não informado.",
    "proteins": 0,
    "foodImage": "https://www.unicamp.br/unicamp/sites/default/files/inline-images/logo_124_0.png",
    "carbohydrates": 0,
    "lipids": 0,
    "likes": 0,
    "calories": 0
  }

  newFoodRef = foodRef.push(foodObj);

  return newFoodRef.key



def runJob1():
  webpage = requests.get(url)
  soup = BeautifulSoup(webpage.content, "html.parser")
  dom = etree.HTML(str(soup))

  refeicoes = soup.find_all("table", class_="fundo_cardapio")


  refeicao=refeicoes[2]

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

  for comida in comidas:
    if checkIfFoodExistsByName(comida) == False:
      addFood(comida)



