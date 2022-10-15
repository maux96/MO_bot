from typing import Tuple, List

from importlib.util import spec_from_file_location, module_from_spec
from BaseProvider import BaseProvider
from BaseSolver import BaseSolver, UserSolution, SolverInfo

from os import listdir
from pathlib import Path

class LocalSolverProvider(BaseProvider):
    def get_solver(self, solver_name: str) -> BaseSolver:
        spec = spec_from_file_location(solver_name,f"src/solvers/{solver_name}.py")
        
        if spec == None or spec.loader == None:
            raise Exception("Solutioner not founded :(")

        module=module_from_spec(spec)
        spec.loader.exec_module(module)
#@TODO  retornar solo la clase, no una instancia de esta...
        return module.defaultSolver() 


    def compare_solution(self, solver_name: str ,user_solution: UserSolution):
        """ 
            Compara la solucion del usuario con la optima retornando un conjunto de
            mensajes de error (si existen) y un conjunto de mensajes dados por el
            solver teniendo en cuenta que tan "lejos" esta su solucion de la optima.
        """
        return self.get_solver(solver_name).get_solver_solution(user_solution)

    def get_solver_info(self, solver_name: str) -> SolverInfo:
        """ Muestra la informacion de un solver (el problema asociado a este ) """
        return self.get_solver(solver_name).get_solver_info()
        

    def enumerate_available(self) -> List[Tuple[str,str]]:
        """ 
            Enumera todos los nombres de cada uno de los problemas 
        """
        names=listdir(Path("src","solvers"))
        sol = []
        for name in names:
            if name[-3:] == ".py":
                title = self.get_solver(name[:-3]).title
                sol.append((title,name[:-3]))
        return sol


