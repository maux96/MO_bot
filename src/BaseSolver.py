from abc import ABC, abstractmethod 
from typing import List, Dict, TypedDict, Any, Tuple

class UserSolution(TypedDict):
    """ La solucion dada por el usuario. """
    id: str
    values: Dict[str,Any] 
    parameters: Dict[str, Any] | None

class SolverInfo(TypedDict):
    """ Informacion de un solver reunida. """

    """ Nombre del problema que sirve de identificador, debe ser unico. """
    name: str

    """ Titulo del problema o nombre completo. """
    title: str

    """ Descripcion del problema. """
    description: str

    """ 
        Variables del problema
        Descripcion asociada a cada variable. 
    """
    variables: Dict[str,str]

    """ 
        Parametros del problema
        Cada parametro es una tupla de el valor por defecto y la descripcion 
        de este.
    """
    parameters: Dict[str,Tuple[Any,str]] 


class BaseSolver(ABC):
    """ 
        Clase Abtracta

        La definicion y solucion de un problema especifico. Las clases 
        herederas deben sobreescribir las variables estaticas de clase tales
        como _name, _title, _text, _default_parameters y 
        _variables_descriptions con los valores asociados al problema.
    """

    _name: str =  ""
    _title: str = ""
    _text: str  = ""

    _default_parameters: Dict[str,Tuple[Any,str]] = {} 
    _variables_descriptions: Dict[str,str]  = {} 

    
    def __init__(self):
        self._errors: List[str]= []
        self._messages: List[str]= []

        if not self.is_info_good():
            raise NotImplementedError("El problema seleccionado no esta completo.")

        self._parameters: Dict[str,Any] = {
            key:value for key,(value,_) in self._default_parameters.items()
        } 
        
    @classmethod
    def is_info_good(cls):
        return bool(cls._name) and \
               bool(cls._title) and \
               bool(cls._text) and  \
               bool(cls._default_parameters) and \
               bool(cls._variables_descriptions)


    
    @property
    def title(cls):
        return cls._title 

    @property
    def text(cls):
        return cls._text

    def get_param_value(self, param_name: str):
        return self._parameters[param_name]

    @classmethod
    def get_solver_info(cls) -> SolverInfo:
        return {
            "name":cls._name,
            "title":cls._title,
            "description":cls._text,
            "variables":cls._variables_descriptions,
            "parameters":cls._default_parameters,
        }


    @abstractmethod
    def _solve_model(self) -> Dict[str, Any]:
        """
            Abstract Method 

            Soluciona el problema de optimizacion y retorna un diccionario con 
            las variables en su estado optimo.
        """

    @abstractmethod
    def _compare_solution(self, solution: Dict[str, Any], best_solution: Dict[str, Any]):
        """
            Abstract Method 

            La idea es que este metodo sea llamado luego de haber calculado la 
            solucion optima para el problema con self._solve_model.
            Este metodo debe guardar en self._errors y self._messages los 
            errores o mensajes asociados a la compracion de la mejor solucion 
            con la dada por el usuario.
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


    def get_solver_solution(self, solution: UserSolution):
        """ 
            Retorna los mensajes o errores predeterminados por el creador del
            Solver que fueron obtenidos en _compare_solution y guardados en 
            self.messages y self._errors respectivamente.
        """

        # verificar que esten todas las variables necesarias
        for var in self._variables_descriptions:
            if var not in solution["values"]:
                raise Exception(f"Mala configuracion de variables, se esperaba\
                                un valor para la variable '{var}'.")

        if solution["parameters"] != None:
            self._parameters = solution["parameters"]
            # verificar que esten todos los parametros necesarios 
            for p in self._default_parameters:
                if p not in self._parameters:
                    raise Exception(f"Mala configuracion de parametros,\
                                    se esperaba el parametro '{p}'.")

        best_solution = self._solve_model() 
        self._compare_solution(solution["values"], best_solution) 

        return self._messages, self._errors

