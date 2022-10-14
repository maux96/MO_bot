from typing import Dict, TypedDict, Any, List

from importlib.util import spec_from_file_location, module_from_spec
from BaseSolver import BaseSolver, UserSolution, SolverInfo

from os import listdir
from pathlib import Path

def get_solver(solver_name: str) -> BaseSolver:
    spec = spec_from_file_location(solver_name,f"src/solvers/{solver_name}.py")
    
    if spec == None or spec.loader == None:
        raise Exception("Solutioner not founded :(")

    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.defaultSolver()


def compare_solution(solver_name: str ,user_solution: UserSolution):
    """ 
        Compara la solucion del usuario con la optima retornando un conjunto de
        mensajes de error (si existen) y un conjunto de mensajes dados por el
        solver teniendo en cuenta que tan "lejos" esta su solucion de la optima.
    """
    return get_solver(solver_name).get_solver_solution(user_solution)

def get_solver_info(solver_name: str) -> SolverInfo:
    """ Muestra la informacion de un solver (el problema asociado a este ) """
    return get_solver(solver_name).get_solver_info()
    

def enumerate_available(id_prefix="/I__") -> List[str]:
    """ 
        Enumera todos los nombres de cada uno de los problemas 
    """
    names=listdir(Path("src","solvers"))
    sol = []
    for name in names:
        title = "Title"
        if name[-3:] == ".py":
            sol.append(f'{title} ({id_prefix+name[:-3]})')
    return sol



