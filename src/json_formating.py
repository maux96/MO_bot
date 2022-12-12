from typing import Any

def json_stringify(obj: Any):
    """
        Convierte un objeto de python a string, a un formato parecido a JSON
        (No es el mismo)
    """
    return _json_stringify(obj,0)

def _json_stringify(obj: Any, deep: int):
    saved_vals = []
    braces: tuple[str,str]
    if isinstance(obj,dict):
        braces=("{","}")
        for item in obj:
            saved_vals.append(f'"{item}":{_json_stringify(obj[item],deep+1)}')
    elif isinstance(obj,list):
        braces=("[","]")
        for item in obj:
            saved_vals.append(f'{_json_stringify(item,deep+1)}')
    else : return  str(obj)


    return braces[0]+"\n"+iden(deep+1)+\
                (",\n"+iden(deep+1)).join(saved_vals)+\
                "\n"+iden(deep)+braces[1]
 
def iden(deep: int):
    return  " "*deep


