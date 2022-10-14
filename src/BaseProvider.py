from typing import Tuple, List
from abc import ABC, abstractmethod

from BaseSolver import SolverInfo, UserSolution

class BaseProvider(ABC):

    @abstractmethod 
    def compare_solution(self, solver_name: str, user_solution: UserSolution) \
        -> Tuple[List[str],List[str]]:
        """ 
        Abstract Method

        Compara la solucion del usuario con la optima retornando un conjunto de
        mensajes de error (si existen) un conjunto de mensajes dados por el
        solver teniendo en cuenta que tan "lejos" esta su solucion de la optima.
        """

    @abstractmethod
    def get_solver_info(self, solver_name: str)-> SolverInfo:
        """ 
        Abstract Method

        Muestra la informacion de un solver (el problema asociado a este ). 
        """

    @abstractmethod
    def enumerate_available(self) -> List[Tuple[str,str]]:
        """
        Abstract Method

        Enumera los solvers disponibles. Retorna una lista de tuplas con el 
        titulo y nombre(identificador) de cada solver disponible.
        """
