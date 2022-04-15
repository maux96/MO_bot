from solvers.dynamic_load import verify_solution 

# dada una solucion a un problema da un veredicto basada en lo que retorna el solver...
def get_veredict(solution : str):
    errors, messages=verify_solution(solution)
    if errors:
        return ("Errores 😓:\n\n-"+ "\n-".join(errors))
    elif  messages:
        return ("Resultados 🤔:\n\n-"+ "\n-".join(messages))
    else: 
        return ("No hay nada que mostrar 😅.... de quién será la culpa 😒... ")
 
