from gekko import GEKKO
from gekko.gk_variable import GKVariable

MODEL_SOLUTION = {}

def _solve_model(model_params : dict[str:int]):
	
	m = GEKKO(remote=False) #Initialize gekko
	#m.options.IMODE = 3
	m.options.SOLVER = 1
	
	proveedores = model_params["proveedores"]	
	vehiculos = model_params["vehiculos"]
	tiempo_desplazamiento = model_params["tiempo_desplazamiento"]
	ingredientes_necesitados = model_params["ingredientes_necesitados"]
	costo_maximo_posible = model_params["costo_maximo_posible"]

	# Constantes
	p_demora =  m.Param([ p["demora"] for p in proveedores],name="p_demora")
	p_demora_por_ingredientes = m.Param([ p["demora_por_ingredientes"] for p in proveedores],name="p_demora_por_ingredientes")
	p_costo_ingredientes = [ 
		m.Param([ (c) for c in p["costo_ingredientes"] ]) for p in proveedores
	]
	v_costo_recorrido = m.Param([c["costo_recorrido"] for c in vehiculos],name="v_costo_recorrido")
	v_costo_fijo = m.Param([ c["costo_fijo"] for c in vehiculos],name="v_costo_fijo")
	tiempo_desplazamiento = m.Const(tiempo_desplazamiento)
	ingredientes_necesitados = m.Param([ i for i in ingredientes_necesitados ],name="ingredientes_necesitados")
	costo_maximo_posible = m.Const(costo_maximo_posible)

	# Variables
	# ingrediente j comprado por el carro k en el proveedor i
	#ingredientes_comprados = [
	#	[ 
	#		[
	#			m.Var(lb=0,ub=i,integer=True,) for i in ingredientes_necesitados  
	#		] for _ in proveedores 
	#	] for _ in vehiculos 
	#]			
	ingredientes_comprados = [
		[ 
			
			m.Var(value=[0]*len(ingredientes_necesitados),lb=0,ub=ingredientes_necesitados,integer=True) for _ in proveedores 
		] for _ in vehiculos 
	]
	## tiempo tomado por el carro k
	#demora_vehiculo = [ m.Var(lb=0) for _ in vehiculos ]

	# costo total 
	#costo_total = m.Var(lb=0,ub=costo_maximo_posible) 

	print("XXXXXXXXXXXXXXXXXXXXXXXXxxXD 1")
	print(vehiculos)	
	print(proveedores)	
	print(ingredientes_necesitados)	
	print("------------")	
	m.Minimize(
		m.sum([ 
			p_costo_ingredientes[i][j]*ingredientes_comprados[k][i][j]   
			for k in range(len(vehiculos)) 
			for i in range(len(proveedores))	
			for j in range(len(ingredientes_necesitados))	
		])# +
#m.sum([ 
#	v_costo_recorrido[k] * contains_no_zero_elements(ingredientes_comprados[k][i])
#	for k in range(len(vehiculos)) 
#	for i in range(len(proveedores))	
#])+ 
#m.sum([ 
#	v_costo_fijo[k] * contains_no_zero_elements(ingredientes_comprados[k])
#	for k in range(len(vehiculos)) 
#])# <= costo_maximo_posible
	)

	print("XXXXXXXXXXXXXXXXXXXXXXXXxxXD 2")
	#Tiempo		
#m.Minimize(
#    max([
#        (
#			m.sum([
#                p_demora_por_ingredientes[i] * ingredientes_comprados[k][i][j]
#                for i in range(len(proveedores))	
#                for j in range(len(ingredientes_necesitados))	
#            ]) + 
#            m.sum([
#                p_demora[i] * contains_no_zero_elements(ingredientes_comprados[k][i]) 
#                for i in range(len(proveedores))	
#                for j in range(len(ingredientes_necesitados))	
#            ])
#		) for k in range(len(vehiculos)) 
#	])
#)	
	m.solve()
	for k in range(len(vehiculos)):
		#MODEL_SOLUTION["carro_"+str(k)] = ingredientes_comprados[k].VALUE[0]
		MODEL_SOLUTION["carro_"+str(k+1)] = ingredientes_comprados[k]



	

def _compare_solution(model_params,gived_solution):

	proveedores = model_params["proveedores"]	
	vehiculos = model_params["vehiculos"]
	tiempo_desplazamiento = model_params["tiempo_desplazamiento"]
	ingredientes_necesitados = model_params["ingredientes_necesitados"]
	costo_maximo_posible = model_params["costo_maximo_posible"]

	costo_generado=0
	for carro in gived_solution:
		k = carro.split('_')[1]
		car_cost = 0 
		movimientos = 0
		for i in ranger(len(gived_solution[carro])):
			cantidad_ingre = 0
			for j in gived_solution[carro][i]:
				car_cost  += proveedores[i]["costo_ingredientes"][j] * gived_solution[carro][i][j]
				if proveedores[i]["costo_ingredientes"][j] * gived_solution[carro][i][j] > 0:
					cantidad_ingre +=1
			movimientos +=1 if cantidad_ingre != 0 else 0
		costo_generado += car_cost
		if car_cost != 0:		
			costo_generado += vehiculos[k]["costo_fijo"]
		if movimientos != 0:		
			costo_generado += vehiculos[k]["costo_recorrido"]*(movimientos+1)
	if costo_generado > costo_maximo_posible: 
		_log_error("La cantidad de dinero no alcanza... los proveedores ven que no eres confiable con el pago y deciden no hacer mas negocios contigo... el negocio fracasa y vas a la quiebra. ")
		_log_error(f"Tenias que pagar: ${costo_generado}")
		_log_error(f"Solo contabas con: ${costo_maximo_posible}")
		return


	demora = demora_total(gived_solution, proveedores, ingredientes_necesitados)	
	print("demora:",demora)

	MODEL_SOLUTION["obj"] =  demora_total(MODEL_SOLUTION, proveedores, ingredientes_necesitados)		
	obj = MODEL_SOLUTION["obj"]
	if demora <= obj < demora*1.1 :
		_log_success_message(f"Esto esta demasiado bien... lograste traer a tiempo todo lo que hacia falta y con un costo aceptable... ahora podremos hacer las pizzas que tantricas que tanto le gustan a nuestros clientes <3 (demora={demora})")			
	elif demora*1.1 < obj < demora*1.3 :
		_log_success_message(f"Aceptable pero puede mejorar... lograste casi que a tiempo nuestros objetivos ... (demora={demora})")			
	elif demora*1.3 < obj < demora*1.6 :
		_log_success_message(f"Menuda demora te has dado... creo que vamos a pensar en contratar a otra persona para este trabajo ... (demora={demora})")			
	elif demora*1.6 < obj :
		_log_success_message(f"Demasiado lento......... ESTAS DESPEDIDO!!! (demora={demora})")			
	else:
		_log_success_message(f"WTF, como fue que llegamos aqui... debe haber ocurrido un error o algo lol(demora={demora})")	


def contains_no_zero_elements(li):
	for e in li: 
		if isinstance(e,GKVariable):
			x = contains_no_zero_elements(e)
			if x == 1:
				return 1
		elif e != 0:
			return 1
	return 0
def demora_total(solution, proveedores, ingredientes_necesitados):
	demora=0
	for carro in solution:
		k = carro.split('_')[1]
		candidato=sum([
			proveedores["demora_por_ingredientes"][i] * solution[carro][i][j]
                    for i in range(len(proveedores))	
                    for j in range(len(ingredientes_necesitados))	
		]) 
		+sum([
			proveedores["demora"][i] * 0 if 0== (len([ingr for ingr in solution[carro][i] if ingr != 0])) else 1
                    for i in range(len(proveedores))	
                    for j in range(len(ingredientes_necesitados))	
                ])
		demora = max(demora,candidato)
	return demora	

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


