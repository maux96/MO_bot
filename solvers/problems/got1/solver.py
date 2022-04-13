from gekko import GEKKO

# lo retornado por el modelo
# va a tener : _errors, _success_messages
MODEL_SOLUTION = {}

#verifica que se hayan puesto los parametros correspondientes
def _verify_params(model_params,gived_solution):
    needs=["hierro","madera","cuero"]    #los totales
    needs+=[ "c_"+char+"_"+ty for char in ["h","m","c"] for ty in ["sword","bow","catapult"]]
    needs+=["sword_damage","bow_damage","catapult_damage"]

    for x in needs:
        if x not in model_params:
            _log_error("Falta el parametro "+x+".")

    needs=["amount_swords","amount_bows","amount_catapults"]
    for x in needs:
        if x not in gived_solution:
            _log_error("Falta la variable "+x+".")



# calcula la solucion optima para el problema dado unos parametros
def _solve_model(model_params : dict[str:int]):

    m = GEKKO(remote=False) #Initialize gekko

    m.options.SOLVER = 1

    iron_units = m.Param(value=model_params["hierro"] )
    wood_units = m.Param(value=model_params["madera"] )
    leather_units = m.Param(value=model_params["cuero"] )

    amount_swords = m.Var(lb = 0,integer=True)
    amount_bows = m.Var(lb = 0,integer=True)
    amount_catapults = m.Var(lb = 0,integer=True)

    #costos
    c_h_sword = model_params["c_h_sword"] 
    c_m_sword = model_params["c_m_sword"] 
    c_c_sword = model_params["c_c_sword"] 
    
    c_h_bow = model_params["c_h_bow"] 
    c_m_bow = model_params["c_m_bow"] 
    c_c_bow = model_params["c_c_bow"] 

    c_h_catapult = model_params["c_h_catapult"] 
    c_m_catapult = model_params["c_m_catapult"] 
    c_c_catapult = model_params["c_c_catapult"] 


    m.Equation(amount_swords*c_h_sword+amount_bows*c_h_bow+amount_catapults*c_h_catapult<=iron_units) #Iron
    m.Equation(amount_swords*c_m_sword+amount_bows*c_m_bow+amount_catapults*c_m_catapult<=wood_units) #Wood
    m.Equation(amount_swords*c_c_sword+amount_bows*c_c_bow+amount_catapults*c_c_catapult<=leather_units) #Leather

    m.Maximize(total_damage(amount_swords,amount_bows,amount_catapults,model_params))

    m.solve(disp = False)

   
    MODEL_SOLUTION["amount_swords"] = amount_swords.VALUE[0]
    MODEL_SOLUTION["amount_bows"] = amount_bows.VALUE[0]
    MODEL_SOLUTION["amount_catapults"] = amount_catapults.VALUE[0]
    MODEL_SOLUTION["obj"]= total_damage(amount_swords.VALUE[0],amount_bows.VALUE[0],amount_catapults.VALUE[0],model_params)

# compara la solucion calculada que esta dentro de MODEL_SOLUTION
# con la sulucion optima del modelo y retorna un input de texto personalizado 
# basado en la diferencia
def _compare_solution(model_params,gived_solution):
    #totales
    t_hierro=model_params["hierro"] 
    t_madera=model_params["madera"] 
    t_cuero=model_params["cuero"] 

    #costos
    c_h_sword = model_params["c_h_sword"] 
    c_m_sword = model_params["c_m_sword"] 
    c_c_sword = model_params["c_c_sword"] 
    
    c_h_bow = model_params["c_h_bow"] 
    c_m_bow = model_params["c_m_bow"] 
    c_c_bow = model_params["c_c_bow"] 

    c_h_catapult = model_params["c_h_catapult"] 
    c_m_catapult = model_params["c_m_catapult"] 
    c_c_catapult = model_params["c_c_catapult"] 

    #mensajes de error personalizados por si no alcanzan los materiales :(
    sword = gived_solution["amount_swords"]
    t_hierro -= sword*c_h_sword
    t_madera -= sword*c_m_sword
    t_cuero -= sword*c_c_sword
    if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
        _log_error("No se pueden construir tantas espadas :(")
        return

    bow = gived_solution["amount_bows"]
    t_hierro -= bow*c_h_bow
    t_madera -= bow*c_m_bow
    t_cuero -=  bow*c_c_bow
    if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
        _log_error("No se pueden construir tantos arcos :(")
        return

    catapult = gived_solution["amount_catapults"]
    t_hierro -= catapult*c_h_catapult
    t_madera -= catapult*c_m_catapult
    t_cuero -=  catapult*c_c_catapult
    if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
        _log_error("No se pueden construir tantas catapultas :(")
        return

    if(sword < 0 or bow < 0 or catapult < 0):
        _log_error('Has creado una cantidad negativa, el mundo implosiona, mision cumplida, los caminantes blancos han muerto')
        return
     
    #calculo de danno 
    damage_dealt =total_damage(sword,bow,catapult,model_params)
    best_posible =MODEL_SOLUTION["obj"]
    _log_success_message(f'Hemos realizado {damage_dealt} daños en las tropas enemigas')
    if damage_dealt < best_posible*0.98:
       _log_success_message(f'Necesitamos {best_posible*0.98 - damage_dealt} de daño para alcanzar la victoria')
    if(damage_dealt > best_posible*0.98):
       _log_success_message('Hemos aniquilado a las tropas enemigas, una rotunda victoria')
    elif(damage_dealt > best_posible*0.8):
       _log_success_message('Estuvimos tan cerca de la victoria, fue un honor luchar a su lado')
    elif(damage_dealt > best_posible*0.5):
       _log_success_message('Al menos eliminamos la mitad de sus tropas')
    elif(damage_dealt < best_posible*0.1):
       _log_success_message('No se como alguien logró hacerlo tan mal')
    else:
       _log_success_message('Que desastre!')

    pass

def _log_error(message):
    if not MODEL_SOLUTION.__contains__("_errors"):
        MODEL_SOLUTION["_errors"]=[]
    MODEL_SOLUTION["_errors"].append(message)

def _log_success_message(message):
    if not MODEL_SOLUTION.__contains__("_success_message"):
        MODEL_SOLUTION["_success_message"]=[]
    MODEL_SOLUTION["_success_message"].append(message)


def total_damage(swords,bows,catapults, model_params):
    s_d = model_params["sword_damage"]
    b_d = model_params["bow_damage"]
    c_d = model_params["catapult_damage"]
    return s_d*swords+b_d*bows+c_d*catapults

def main():
    _verify_params(model_params,gived_solution)
    if MODEL_SOLUTION.__contains__("_errors") and len(MODEL_SOLUTION["_errors"])>0:
        return   

    _solve_model(model_params)
    _compare_solution(model_params,gived_solution)

main()

