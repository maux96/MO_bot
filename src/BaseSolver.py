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

        La definicion y solucion de un problema especifico.
    """
    def __init__(self):
        self._errors: List[str]= []
        self._messages: List[str]= []

        self._default_parameters: Dict[str,Tuple[Any,str]] = {} 
        self._variables_descriptions: Dict[str,str] = {}
        self._set_default_params_and_variables()
        self._parameters: Dict[str,Any] = {
            key:value for key,(value,_) in self._default_parameters.items()
        } 

        self._name: str = "DefaultName" 
        self._title="DefaultTitle"
        self._text="DefaultText"
        self._set_default_info()

    
    @property
    def title(self):
        return self._title 

    @property
    def text(self):
        return self._text

    def get_param_value(self, param_name: str):
        return self._parameters[param_name]


    def get_solver_info(self) -> SolverInfo:
        return {
            "name":self._name,
            "title":self._title,
            "description":self._text,
            "variables":self._variables_descriptions,
            "parameters":self._default_parameters,
        }


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
    def _set_default_params_and_variables(self):
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

        best_solution = self._solve_model(solution) 
        self._compare_solution(best_solution) 

        return self._messages, self._errors

