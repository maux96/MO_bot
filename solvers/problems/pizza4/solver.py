from gekko import GEKKO

MODEL_SOLUTION = {}

def _solve_model(model_params : dict[str:int]):
	
	m = GEKKO(remote=False) #Initialize gekko
	m.options.SOLVER = 1
	
	#Agregos
	agregos = model_params["agregos"]	
	a_afrodisiaco = { a["nombre"]:m.Const(value=a["afrodisiaco"]) for a in agregos } 
	a_energia = { a["nombre"]:m.Const(value=a["energia"]) for a in agregos } 
    #ignoremos el gusto por ahora ...
	#a_gusta = { a["nombre"]:m.Param(value=a["gusta"]) for a in agregos } 
	a_costo = { a["nombre"]:m.Const(value=a["costo"]) for a in agregos } 
	precio_base = m.Const(model_params["precio_base"])
	#Cantidad de Agregos comprados de cada tipo
	a_comprado= { a["nombre"]:m.Var(lb=0, integer=True) for a in agregos } 

	participantes = model_params["participantes"]		
	p_llenura_inicial= { p["nombre"]:m.Param(value=p["llenura_inicial"]) for p in participantes } 
	p_minima_llenura= { p["nombre"]:m.Param(value=p["minima_llenura"]) for p in participantes } 
	p_maxima_llenura= { p["nombre"]:m.Param(value=p["maxima_llenura"]) for p in	participantes } 
	p_dinero= { p["nombre"]:m.Param(value=p["dinero"]) for p in participantes } 
	p_exitacion_inicial= { p["nombre"]:m.Param(value=p["exitacion_inicial"]) for p in participantes } 


	# llenura
	llenura = sum([ a_energia[a] * a_comprado[a] for a in  a_comprado ]) 
	m.Equation(sum([ p_maxima_llenura[p] for p in p_maxima_llenura]) >= llenura )
	m.Equation(llenura >= sum([ p_minima_llenura[p] for p in p_minima_llenura]) )
	
	# dinero
	m.Equation(precio_base + sum([ a_costo[a] * a_comprado[a] for a in  a_comprado ]) <= sum([ p_dinero[p] for p in p_dinero]))


	m.Maximize(exitacion_total(a_comprado, a_afrodisiaco, p_exitacion_inicial))
	m.solve(disp=False)

	for a in a_comprado:
		MODEL_SOLUTION[a] = a_comprado[a].VALUE[0]


def exitacion_total(a_comprado, a_afrodisiaco, exitacion_inicial):
	return sum([a_afrodisiaco[a] * a_comprado[a] for a in a_comprado]) + sum([ exitacion_inicial[p] for p in exitacion_inicial])

def _compare_solution(model_params,gived_solution):

	agregos = model_params["agregos"]	
	participantes = model_params["participantes"]	
	
	a_afrodisiaco = { a["nombre"]:a["afrodisiaco"] for a in agregos } 
	a_energia = { a["nombre"]:a["energia"] for a in agregos } 
	a_costo = { a["nombre"]:a["costo"] for a in agregos } 

	p_exitacion_inicial= { p["nombre"]:p["exitacion_inicial"] for p in participantes } 
	

	suma_de_dinero_necesaria = model_params["precio_base"]+ sum([gived_solution[a]*a_costo[a] for a in gived_solution ])		
	suma_dinero_todos = sum( [p["dinero"] for p in participantes ])		
	if suma_dinero_todos < suma_de_dinero_necesaria:
		_log_error("La cantidad de dinero no alcanza, tratan de convencer al que trae las pizzas para que se una a la diversion y asi pagarle la pizza, este al darse cuenta, va a la policia y los denuncia por acoso sexual, ahora estan todos presos y todo por no contar bien el dinero :(")
		_log_error(f" Necesario: ${suma_de_dinero_necesaria} ")
		_log_error(f" Recaudado: ${suma_dinero_todos} ")
		return
	
	suma_energia_conseguida = sum([	gived_solution[a]*a_energia[a] for a in gived_solution ])	
	min_acum = 0
	max_acum = 0
	for p in participantes:	
		min_acum += p["minima_llenura"]
		max_acum += p["maxima_llenura"]
		if min_acum > suma_energia_conseguida:	
			_log_error(f"Oh no..., despues de haber comenzado la cuestion... parece que {p['nombre']}  no comio lo suficiente ... y se desmayo, todo el mundo del susto, salio corriendo.... que desastre! ")
			_log_error(f"Energia conseguida repartida: {suma_energia_conseguida}")
			_log_error("Necesitas comprar mas comida.")
			return
	if max_acum < suma_energia_conseguida: 
		_log_error(f"Oh no..., parece que {p['nombre']}  comio demasiado  porque le dejaron comida extra... y como buen golozo que es no la podia botar, lo que resulto que en el medio del acto comenzara a vomitar!! todo el mundo ,de la repugnancia, se van a su casa con la noche arruinada.... que desastre!")
		return
	
	exitacion=exitacion_total(gived_solution , a_afrodisiaco, p_exitacion_inicial)		
	print("exitacion:",exitacion)

	MODEL_SOLUTION["obj"] =  exitacion_total(MODEL_SOLUTION, a_afrodisiaco, p_exitacion_inicial)
	obj = MODEL_SOLUTION["obj"]
	if exitacion < obj/3:
		_log_success_message(f"No se que intentaron entre {len(participantes)} participantes para que saliera tan mal,a nadie le gusto, fue un desastre! (exitacion={exitacion})")			
	elif exitacion < obj/2 :
		_log_success_message(f"Poca gente la paso bien hoy, creo que deberian entretenerse en otra cosa, aun asi hay quien disfruto!(exitacion={exitacion})")			
	elif exitacion < obj/1.1 :
		_log_success_message(f"En general no estuvo mal, pero puede mejorar... vamos a esforzarnos un poco mas para la proxima (exitacion={exitacion})")			
	elif obj/1.1 <=  exitacion < obj :
		_log_success_message(f"Todo parece indicar que todo el mundo disfruto gracias a la buena aliementacion, hay que repetir la fiesta pronto!! :D (exitacion={exitacion})")	
	elif exitacion == obj :
		_log_success_message(f"ESA PIZZA ERA DE LOS DIOSES!! logras la maxima exitacion!!! Todos se quedan con ganas y estan ansiosos por repetir la fiesta!! (exitacion={exitacion})")	
	else:
		_log_success_message("WTF, como fue que llegamos aqui... debe haber ocurrido un error o algo lol(exitacion={exitacion})")	


def _log_error(message):
    if not MODEL_SOLUTION.__contains__("_errors"):
        MODEL_SOLUTION["_errors"]=[]
    MODEL_SOLUTION["_errors"].append(message)
def _log_success_message(message):
    if not MODEL_SOLUTION.__contains__("_success_message"):
        MODEL_SOLUTION["_success_message"]=[]
    MODEL_SOLUTION["_success_message"].append(message)




def main():
	#_verify_params(model_params,gived_solution)
	#if MODEL_SOLUTION.__contains__("_errors") and len(MODEL_SOLUTION["_errors"])>0:
	#    return   
	_solve_model(model_params)
	_compare_solution(model_params,gived_solution)
main()


