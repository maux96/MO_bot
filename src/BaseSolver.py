from abc import ABC, abstractmethod 
from typing import List, Dict, TypedDict, Any, Tuple

class UserSolution(TypedDict):
    """ La solucion dada por el usuario. """
    id: str
    values: Dict[str,Any] 
    parameters: Dict[str, Any] | None


class BaseSolver(ABC):
    """ 
        Clase Abtracta

        La definicion y solucion de un problema especifico.
    """
    def __init__(self):
        self._errors: List[str]= []
        self._messages: List[str]= []

        self._default_parameters: Dict[str,Tuple[Any,str]] = {} 
        self._set_default_params()

        self._title="DefaultTitle"
        self._text="DefaultText"
        self._set_default_info()

    
    @property
    def Title(self):
        return self._title 

    @property
    def Text(self):
        return self._text

    def GetParamValue(self, param_name: str):
        return self._default_parameters[param_name]

    def GetParameters(self):


    @abstractmethod
    def _solve_model(self, solution: UserSolution) -> Dict[str, Any]:
        """
            Abstract Method 

            Soluciona el problema de optimizacion y retorna un diccionario con 
            las variables en su estado optimo.
        """

    @abstractmethod
    def _compare_solution(self, solution: Dict[str, Any]):
        """
            Abstract Method 

            La idea es que este metodo sea llamado luego de haber calculado la 
            solucion optima para el problema con self._solve_model.
            Este metodo debe guardar en self._errors y self._messages los 
            errores o mensajes asociados a la compracion de la mejor solucion 
            con la dada por el usuario.
        """
        
    @abstractmethod
    def _set_default_params(self):
        """ 
            Abstract Method 
            
            Establece los parametros por defecto del problema en cuestion.
        """

    @abstractmethod
    def _set_default_info(self):
        """
            Abstract Method

            Establece el titulo y explicacion del problema en cuestion.
        """

    def _log_error(self, message: str):
        """ 
            Guarda un mensaje de error que se obtuvo en la comparacion de la
            solucion optima con la solucion del usuario. 
        """
        self._errors.append(message)

    def _log_message(self, message: str):
        """ 
            Guarda un mensaje que se obtuvo en la comparacion de la solucion  
            optima con la solucion del usuario. 
             
        """
        self._messages.append(message)

    def set_params(self, params: Dict[str, Any]):
        """ Set specific paramteres for the solver. """
        raise Exception("Not Implemented!") 

    def get_solver_solution(self, solution: UserSolution):
        """ 
            Retorna los mensajes o errores predeterminados por el creador del
            Solver que fueron obtenidos en _compare_solution y guardados en 
            self.messages y self._errors respectivamente.
        """
        best_solution = self._solve_model(solution) 
        self._compare_solution(best_solution) 

        return self._messages, self._errors

