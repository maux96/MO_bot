from BaseSolver import UserSolution
from config import solver_provider
import json

def get_veredict(solution: str):
    user_solution: UserSolution =json.loads(solution) 
    solver_name :str=user_solution["id"]
    messages, errors = solver_provider.compare_solution(solver_name,user_solution)

    if errors:
        return ("Errores 😓:\n\n-"+ "\n-".join(errors))
    elif messages:
        return ("Resultados 🤔:\n\n-"+ "\n-".join(messages))
    else: 
        return ("No hay nada que mostrar 😅.... de quién será la culpa 😒... ")
 
