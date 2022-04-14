from pathlib import Path
from json import load 
from io import StringIO
from os import listdir

def verify_solution(uploaded_json : str) :
    gived_solution=load(StringIO(uploaded_json))
    print(gived_solution)
    return dynamic_load(gived_solution["_id"],gived_solution["_values"])

#retorna una lista de errores y  una lista de mensajes para el usuario dado un id
def dynamic_load(file_name : str, gived_solution : dict ,model_params:dict=None) -> (list[str],list[str]): 

    
    path=Path("solvers","problems",file_name,"solver.py")

    with open(path,"rb") as source:
        comp = compile(source.read(),"solver.py","exec")

    if model_params == None:
        default_params=Path("solvers","problems",file_name,"defaults.json")
        with open(default_params,"r") as json:
            model_params=load(json)


    _locals = {"model_params":model_params,"gived_solution":gived_solution}
    exec(comp,_locals)
    print(_locals["MODEL_SOLUTION"]) 

    errors = _locals["MODEL_SOLUTION"]["_errors"] if _locals["MODEL_SOLUTION"].__contains__("_errors") else [] 
    success =_locals["MODEL_SOLUTION"]["_success_message"] if _locals["MODEL_SOLUTION"].__contains__("_success_message") else [] 

    return  errors, success


# enumera todos los identificadores de cada uno de los problemas
def enumerate_solvers(id_prefix="/I__"):
    ids=listdir(Path("solvers","problems"))
    sol = []
    for id in ids:
        with open(Path("solvers","problems",id,"info.json")) as json:
            sol.append(f'{load(json)["title"]} ({id_prefix+id})')
    return sol

# retorna un {} de la forma {'id':id,'title':title,'text':text}
def get_solver_info(id):
    with open(Path("solvers","problems",id,"info.json")) as json:
        sol= load(json)
    return sol        

if __name__ == "__main__":
    #print(dynamic_load("got1", {"amount_swords":54167,"amount_bows":29165,"amount_catapuls":0,}))
    pass

