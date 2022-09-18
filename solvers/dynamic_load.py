from pathlib import Path
from json import load, dumps
from io import StringIO
from os import listdir
from typing import List, Tuple, TypedDict
from bs4 import BeautifulSoup
from collections import namedtuple
from some_types import ProblemInfo,VarDescript

def verify_solution(uploaded_json : str) :
    gived_solution=load(StringIO(uploaded_json))
    model_parameters = None
    if gived_solution.__contains__("_parameters"):
        model_parameters = gived_solution["_parameters"] 
    #print(gived_solution)
    return dynamic_load(gived_solution["_id"],gived_solution["_values"], model_parameters)

def dynamic_load(file_name : str, gived_solution : dict ,model_params:dict=None) -> Tuple[List[str],List[str]]: 
    """ Retorna una lista de errores y  una lista de mensajes para el usuario dado un id """

    path=Path("solvers","problems",file_name,"solver.py")

    with open(path,"rb") as source:
        comp = compile(source.read(),"solver.py","exec")

    if model_params == None:
        default_params=Path("solvers","problems",file_name,"defaults.json")
        with open(default_params,"r") as json:
            model_params=load(json)


    _locals = {"model_params":model_params,"gived_solution":gived_solution}
    exec(comp,_locals)
    #print(_locals["MODEL_SOLUTION"]) 

    errors = _locals["MODEL_SOLUTION"]["_errors"] if _locals["MODEL_SOLUTION"].__contains__("_errors") else [] 
    success =_locals["MODEL_SOLUTION"]["_success_message"] if _locals["MODEL_SOLUTION"].__contains__("_success_message") else [] 

    return  errors, success


 
def enumerate_solvers(id_prefix="/I__") -> List[str]:
    """ 
        Enumera todos los identificadores de cada uno de los problemas 
    """
    ids=listdir(Path("solvers","problems"))
    sol = []
    for id in ids:
        with open(Path("solvers","problems",id,"info.json")) as json:
            sol.append(f'{load(json)["title"]} ({id_prefix+id})')
    return sol

# retorna un {} de la forma {'id':id,'title':title,'text':text}
def get_solver_info(id: str) -> ProblemInfo :
    """ 
        Busca en la carpeta asociada al problema con identificador `id` una descripcion del problema,
        esta puede estar en JSON o XML, prioriza XML
    """
    sol=None
    try: 
        sol=read_xml_info(id) 
    except:  
        sol=read_json_info(id)

    return sol

def read_json_info(id: str) -> ProblemInfo :
    """ 
        Lee un archivo JSON con la información del problema con identificador==`id` 
    """
    with open(Path("solvers","problems",id,"info.json")) as json:
        sol=load(json)
    return sol 

def read_xml_info(id: str) -> ProblemInfo :
    """ 
        Los archivos XML son un poco mas sencillos de escribirlos manualmente q los json.
        Por eso se agregó este metodo.
    """
    with open(Path("solvers","problems",id,"info.xml"), "r") as fd:
        soup=BeautifulSoup(fd,"xml")
        sol={}
        sol["id"]: str=soup.find("id").get_text()
        sol["title"]: str=soup.find("title").get_text()
        sol["text"]: str=soup.find("text").get_text()
        sol["used_vars"]: List[VarDescript]=[]
        for var in soup.find_all("variable"):
            sol["used_vars"].append({
                "name":var.attrs["name"],
                "text":var.get_text()
            })
        sol["used_params"]: List[VarDescript]=[]
        for param in soup.find_all("parameter"):
            sol["used_params"].append({
                "name":param.attrs["name"],
                "text":param.get_text()
            })
    return sol

    


if __name__ == "__main__":
    #print(dynamic_load("got1", {"amount_swords":54167,"amount_bows":29165,"amount_catapuls":0,}))
    pass

