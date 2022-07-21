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
	tiempo_maximo_posible = model_params["tiempo_maximo_posible"]


	total_ingredientes = len(ingredientes_necesitados)
	total_vehiculos = len(vehiculos)
	total_proveedores = len(proveedores)

	# Constantes
	p_demora =  [ m.Const(p["demora"]) for p in proveedores]
	p_demora_por_ingredientes = [ m.Const(p["demora_por_ingredientes"]) for p in proveedores]
	p_costo_ingredientes = [ 
		m.Const(c) 
			for p in proveedores
            for c in p["costo_ingredientes"] 
	]
	v_costo_recorrido = [ m.Const(c["costo_recorrido"]) for c in vehiculos]
	v_costo_fijo = [ m.Const(c["costo_fijo"]) for c in vehiculos]
	tiempo_desplazamiento = m.Const(tiempo_desplazamiento)
	ingredientes_necesitados = [ m.Const(i) for i in ingredientes_necesitados ]
	tiempo_maximo_posible = m.Const(tiempo_maximo_posible)


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
		 
        m.Var(lb=0,ub=i,integer=True) 
			for _ in vehiculos 
            for _ in proveedores 
            for i in ingredientes_necesitados 
	]
	## tiempo tomado por el carro xk
	#demora_vehiculo = [ m.Var(lb=0) for _ in vehiculos ]

	# costo total 
	#costo_total = m.Var(lb=0,ub=tiempo_maximo_posible) 

		

	m.Minimize(
		m.sum([ 
			p_costo_ingredientes[i*total_ingredientes + j]*ingredientes_comprados[k*total_proveedores + i*total_ingredientes+ j]   
			for k in range(total_vehiculos) 
			for i in range(total_proveedores)	
			for j in range(total_ingredientes)	
		]) +
		m.sum([ 
			v_costo_recorrido[k] * m.sign2(m.sum(ingredientes_comprados[k*total_proveedores + i*total_ingredientes:k*total_proveedores + (i+1)*total_ingredientes]))
			for k in range(len(vehiculos)) 
			for i in range(len(proveedores))	
		])+ 
		m.sum([ 
			v_costo_fijo[k] * m.sign2(m.sum(ingredientes_comprados[k*total_proveedores:(k+1)*total_proveedores ]))
			for k in range(len(vehiculos)) 
		])
	)


	m.Equations(
	    [	#Todos los carros tienen que haber terminado antes de que se alcance el maximo tiempo....
	        (
				(m.sum([
	                p_demora_por_ingredientes[i] * ingredientes_comprados[k*total_proveedores+i*total_ingredientes+j]
	                for i in range(total_proveedores)	
	                for j in range(total_ingredientes)	
	            ]) + 
	            m.sum([
	                ( tiempo_desplazamiento + p_demora[i] ) * m.sign2(m.sum((ingredientes_comprados[k*total_proveedores+ i*total_ingredientes:k*total_proveedores+ (i+1)*total_ingredientes])))
	                for i in range(total_proveedores)	
	                for j in range(total_ingredientes)	
	            ]) + 
				tiempo_desplazamiento*m.sign2(m.sum([ # el tiempo de retornar a la pizzeria :D
	                m.sign2(m.sum(ingredientes_comprados[k*total_proveedores+ i*total_ingredientes:k*total_proveedores+ (i+1)*total_ingredientes]))
	                for i in range(total_proveedores)	
	                for j in range(total_ingredientes)	
	            ])))<= tiempo_maximo_posible
			) for k in range(len(vehiculos)) 
		] +
		[	# La suma de los ingredientes tiene que ser la necesitada
			m.sum([
			  ingredientes_comprados[k*total_proveedores + i*total_ingredientes + j]
			  for k in range(total_vehiculos)
			  for i in range(total_proveedores)	
			]) == ingredientes_necesitados[j]
		] for j in range(total_ingredientes)
	)	



	m.solve(disp=False)

	for k in range(len(vehiculos)):
		#MODEL_SOLUTION["carro_"+str(k)] = ingredientes_comprados[k].VALUE[0]
		temp = []
		for i in range(len(proveedores)):
			temp.append(list(map(lambda x: x.VALUE[0],ingredientes_comprados[k*total_proveedores+i*total_ingredientes:k*total_proveedores+(i+1)*total_ingredientes])))
		MODEL_SOLUTION["carro_"+str(k+1)] = temp
		print("carro_"+str(k+1),temp)

	

def _compare_solution(model_params,gived_solution):

	proveedores = model_params["proveedores"]	
	vehiculos = model_params["vehiculos"]
	tiempo_desplazamiento = model_params["tiempo_desplazamiento"]
	ingredientes_necesitados = model_params["ingredientes_necesitados"]
	tiempo_maximo_posible = model_params["tiempo_maximo_posible"]


	costo_total,demora_total, errors=calculo_de_solucion(gived_solution, model_params,save_in_log=True)
	if errors: 
		return 
	
	coste_correcto, demora_correcta,_ = calculo_de_solucion(MODEL_SOLUTION, model_params,save_in_log=False) 
	MODEL_SOLUTION["obj"] = coste_correcto 
	if coste_correcto == costo_total :
		_log_success_message(f"Simplemente brutal, lograste el gasto minimo..., gracias a ti podremos entregar las tan queridas pizzas a tiempo y nos va a dar muuuuucho negocio :D (costo={costo_total}, demora={demora_total})")			
	elif coste_correcto <= costo_total < coste_correcto*1.1 :
		_log_success_message(f"Esto esta demasiado bien... lograste traer a tiempo todo lo que hacia falta y con un costo aceptable... ahora podremos hacer las pizzas que tantricas que tanto le gustan a nuestros clientes <3 (costo={costo_total})")			
	elif coste_correcto*1.1 <= costo_total < coste_correcto*1.2 :
		_log_success_message(f"Aceptable pero puede mejorar...gastaste un poco mas de la cuenta pero pasa... (costo={costo_total})")			
	elif coste_correcto*1.2 <= costo_total < coste_correcto*1.5 :
		_log_success_message(f"Menudo gasto... creo que vamos a pensar en contratar a otra persona para este trabajo ... (costo={costo_total})")			
	elif coste_correcto*1.5 <= costo_total :
		_log_success_message(f"Cumpliste los objetivos si, pero de la peor manera posible! ESTAS DESPEDIDO!!! (costo={costo_total})")			
	else:
		_log_success_message(f"WTF, como fue que llegamos aqui... debe haber ocurrido un error o algo lol (costo={costo_total})")	


def calculo_de_solucion(gived_solution,model_params, save_in_log=True):

	proveedores = model_params["proveedores"]	
	vehiculos = model_params["vehiculos"]
	tiempo_desplazamiento = model_params["tiempo_desplazamiento"]
	ingredientes_necesitados = model_params["ingredientes_necesitados"]
	tiempo_maximo_posible = model_params["tiempo_maximo_posible"]


	costo_total=0
	ingredientes_total=[0]*len(ingredientes_necesitados)	
	demora_total=0
	errors=False

	#comprobar que el tiempo gastado sea menor que el minimo a gastar 
	for carro in gived_solution:
		k = int(carro.split('_')[1])-1
		car_cost = 0 
		movimientos = 0
		demora = 0
		for i in range(len(gived_solution[carro])):
			cantidad_ingre = 0
			for j in range(len(gived_solution[carro][i])):
				car_cost  += proveedores[i]["costo_ingredientes"][j] * gived_solution[carro][i][j]
				if proveedores[i]["costo_ingredientes"][j] * gived_solution[carro][i][j] > 0:
					cantidad_ingre +=1
					ingredientes_total[j]+=gived_solution[carro][i][j]
			movimientos +=1 if cantidad_ingre != 0 else 0
			if cantidad_ingre>0:
				demora+=cantidad_ingre*proveedores[i]["demora_por_ingredientes"]
				demora+=proveedores[i]["demora"]

		costo_total += car_cost
		if car_cost != 0:		
			costo_total += vehiculos[k]["costo_fijo"]
		if movimientos != 0:		
			costo_total += vehiculos[k]["costo_recorrido"]*(movimientos+1)
			demora += tiempo_desplazamiento*(movimientos+1)

		if demora > tiempo_maximo_posible and save_in_log: 
			_log_error(f"El vehiculo {carro} se demoro demasiado, eso esta mal, la pizza nunca podra ser hecha a tiempo, como resultado tus clientes no te pagan por llegar tarde..., te comes las pizzas que ya nadie quiere (por lento) en la agonia de no haber recaudado ni un kilo...")
			errors=True
		demora_total = max(demora,demora_total)

	if save_in_log:
		for j in range(len(ingredientes_necesitados)):
			if ingredientes_necesitados[j] != ingredientes_total[j]:
				_log_error("Ni siquiera fuiste capaz de comprar la cantidad de ingredientes necesarios ?")
				_log_error(f"Eran necesaria una cantidad de {ingredientes_necesitados[j]} del ingrediente {j}.")
				_log_error(f"Compraste {ingredientes_total[j]} del ingrediente  {j}.")
				errors = True

	if MODEL_SOLUTION.__contains__("_errors") and MODEL_SOLUTION["_errors"] and save_in_log:
		_log_error(f"El tiempo maximo posible es: {tiempo_maximo_posible}")
		_log_error(f"El vehiculo {carro} demoro: {demora}")
		errors = True

	return costo_total,demora_total, errors


def demora_total(solution, proveedores, ingredientes_necesitados):
	demora=0
	for carro in solution:
		k = int(carro.split('_')[1])-1
		candidato=sum([
			proveedores[i]["demora_por_ingredientes"] * solution[carro][i][j]
                    for i in range(len(proveedores))	
                    for j in range(len(ingredientes_necesitados))	
		]) 
		+sum([
			proveedores[i]["demora"] * 0 if 0== (len([ingr for ingr in solution[carro][i] if ingr != 0])) else 1
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


