from gekko.gekko import GKVariable
from BaseSolver import BaseSolver, UserSolution
from typing import Dict, Any 
from gekko import GEKKO


class PizzasTantricasSolver(BaseSolver):

    _name="pizza1"
    _title="Pizzas Tantricas"
    _text="""Una pareja quiere tener sexo, pero tiene hambre. Para resolver ese problema, deciden encargar la "mejor pizza posible", y para ello llaman a su pizzerı́a favorita que te permite encargar exactamente la pizza que quieras. Ellos solo ponen una base que tiene un costo de 200, y a partir de ahı́ tú escoges qué agregos le quieres poner :-). De cada agrego conoces: cuán afrodisiaco es, cuánto sueño provoca, cuánta energı́a proporciona (o sea, cuánto llena) y el costo que tiene. Además, de cada participante se conoce su "llenura (o hambre, o energı́a) inicial", sus umbrales mı́nimos y máximos de llenura (si te pasas del máximo te da sueño y si no llegas al mı́nimo la cosa no funciona), su umbral de sueño y su excitación inicial. Tambien se conoce el dinero del que dispone cada persona. Se quiere diseñar la mejor pizza posible.
Sabemos de cada ingrediente que: 
  El queso (afrodisiaco:5, energia:7, costo: 150),
  El jamon (afrodisiaco:7, energia:10, costo: 200),
  El cebolla (afrodisiaco:3, energia:5,  costo: 100),
  El camaron (afrodisiaco:15, energia:7, costo: 300) 
Sabemos de los integrantes que:
  Clotilde (llenura inicial:50,minima llenura:10,maxima llenura:100,dinero:400,exitacion inicial:30),
  Federico (llenura inicial:50,minima llenura:5, maxima llenura:100,dinero:500,exitacion inicial:40),
  Alejandre(llenura inicial:50,minima llenura:15,maxima llenura:150,dinero:200,exitacion inicial:50)


PD: Este solver es dinamico, cuando se modifican las parametros es posible cambiar la cantiadad de agregos y de personas, cada una con sus caracteristicas, por lo que es necesario poner las variables dentro de otra variable en este caso "agregos_comprados".
    """
    _default_parameters = {
        "precio_base":(200,"El precio base de la Pizza"),
        
        "agregos":([
            {"nombre": "queso" ,"afrodisiaco":5,"energia":7,"costo": 150},
            {"nombre": "jamon" ,"afrodisiaco":7,"energia":10,"costo": 200},
            {"nombre": "cebolla","afrodisiaco":3,"energia":5,"costo": 100},
            {"nombre": "camaron","afrodisiaco":15,"energia":7,"costo": 300}
        ],"Todos los agregos con sus respectivas caracteristicas:\n`{\n\t'nombre':String,\n\t'afrodisiaco':Number,\n\t'sueño':Number,\n\t'energia':Number,\n\t'costo':Number\n}`"),
        "participantes":([
		{"nombre":"Clotilde", "minima_llenura":10,"maxima_llenura":100,"dinero":400,"exitacion_inicial":30},
		{"nombre":"Federico", "minima_llenura":5,"maxima_llenura":100,"dinero":500,"exitacion_inicial":40},
		{"nombre":"Alejandre","minima_llenura":15,"maxima_llenura":150,"dinero":200,"exitacion_inicial":50}
	    ],"Todos los participantes con sus respectivas caracteristicas\n`{\n\t'nombre':String,\n\t'minima_llenura':Number,\n\t'maxima_llenura':Number,\n\t'dinero':Number,\n\t'exitacion_inicial':Number\n}`")

    }
    _variables_descriptions= {
        "agregos_comprados":("Diccionario de cantidad Agregos comprados.",
                             {"queso":"TU_SOLUCION", "jamon":"TU_SOLUCION",
                              "cebolla":"TU_SOLUCION", "camaron":"TU_SOLUCION"})
    }


    def _solve_model(self):

        m = GEKKO(remote=False) #Initialize gekko
        m.options.SOLVER = 1
        
        #Agregos
        agregos = self.get_param_value("agregos")
        a_afrodisiaco = { a["nombre"]:m.Const(value=a["afrodisiaco"]) for a in agregos } 
        a_energia = { a["nombre"]:m.Const(value=a["energia"]) for a in agregos } 
        a_costo = { a["nombre"]:m.Const(value=a["costo"]) for a in agregos } 
        precio_base = m.Const(self.get_param_value("precio_base"))
        #Cantidad de Agregos comprados de cada tipo
        a_comprado= { a["nombre"]:m.Var(lb=0, integer=True) for a in agregos } 

        participantes = self.get_param_value("participantes")
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


        m.Maximize(self.exitacion_total(a_comprado, a_afrodisiaco, p_exitacion_inicial))



        m.solve(disp=False)
         
        return { a:a_comprado[a].VALUE[0] for a in a_comprado } 

    def exitacion_total(self,a_comprado, a_afrodisiaco, exitacion_inicial):
        return sum([a_afrodisiaco[a] * a_comprado[a] for a in a_comprado]) + sum([ exitacion_inicial[p] for p in exitacion_inicial])

    def _compare_solution(self, solution: Dict[str,Any], best_solution: Dict[str,Any]):

        solution = solution["agregos_comprados"]
        agregos = self.get_param_value("agregos")	
        participantes = self.get_param_value("participantes")
        
        a_afrodisiaco = { a["nombre"]:a["afrodisiaco"] for a in agregos } 
        a_energia = { a["nombre"]:a["energia"] for a in agregos } 
        a_costo = { a["nombre"]:a["costo"] for a in agregos } 
        
        p_exitacion_inicial= { p["nombre"]:p["exitacion_inicial"] for p in participantes } 
        
        
        suma_de_dinero_necesaria = self.get_param_value("precio_base")+ sum([solution[a]*a_costo[a] for a in solution ])		
        suma_dinero_todos = sum( [p["dinero"] for p in participantes ])		
        if suma_dinero_todos < suma_de_dinero_necesaria:
            self._log_error("La cantidad de dinero no alcanza, tratan de convencer al que trae las pizzas para que se una a la diversion y asi pagarle la pizza, este al darse cuenta, va a la policia y los denuncia por acoso sexual, ahora estan todos presos y todo por no contar bien el dinero :(")
            self._log_error(f" Necesario: ${suma_de_dinero_necesaria} ")
            self._log_error(f" Recaudado: ${suma_dinero_todos} ")
            return
        
        suma_energia_conseguida = sum([	solution[a]*a_energia[a] for a in solution ])	
        min_acum = 0
        max_acum = 0
        for p in participantes:	
            min_acum += p["minima_llenura"]
            max_acum += p["maxima_llenura"]
            if min_acum > suma_energia_conseguida:	
                self._log_error(f"Oh no..., despues de haber comenzado la cuestion... parece que {p['nombre']}  no comio lo suficiente ... y se desmayo, todo el mundo del susto, salio corriendo.... que desastre! ")
                self._log_error(f"Energia conseguida repartida: {suma_energia_conseguida}")
                self._log_error("Necesitas comprar mas comida.")
                return
        if max_acum < suma_energia_conseguida: 
            self._log_error(f"Oh no..., parece que {p['nombre']}  comio demasiado  porque le dejaron comida extra... y como buen golozo que es no la podia botar, lo que resulto que en el medio del acto comenzara a vomitar!! todo el mundo ,de la repugnancia, se van a su casa con la noche arruinada.... que desastre!")
            return
        
        exitacion=self.exitacion_total(solution , a_afrodisiaco, p_exitacion_inicial)		
        
        obj = self.exitacion_total(best_solution, a_afrodisiaco, p_exitacion_inicial)
        if exitacion < obj/3:
            self._log_message(f"No se que intentaron entre {len(participantes)} participantes para que saliera tan mal,a nadie le gusto, fue un desastre! (exitacion={exitacion})")			
        elif exitacion < obj/2 :
            self._log_message(f"Poca gente la paso bien hoy, creo que deberian entretenerse en otra cosa, aun asi hay quien disfruto!(exitacion={exitacion})")			
        elif exitacion < obj/1.1 :
            self._log_message(f"En general no estuvo mal, pero puede mejorar... vamos a esforzarnos un poco mas para la proxima (exitacion={exitacion})")			
        elif obj/1.1 <=  exitacion < obj :
            self._log_message(f"Todo parece indicar que todo el mundo disfruto gracias a la buena aliementacion, hay que repetir la fiesta pronto!! :D (exitacion={exitacion})")	
        elif exitacion == obj :
            self._log_message(f"ESA PIZZA ERA DE LOS DIOSES!! logras la maxima exitacion!!! Todos se quedan con ganas y estan ansiosos por repetir la fiesta!! (exitacion={exitacion})")	
        else:
            self._log_message("WTF, como fue que llegamos aqui... debe haber ocurrido un error o algo lol(exitacion={exitacion})")	

    def total_damage(self, swords: int | GKVariable, bows: int | GKVariable, catapults: int | GKVariable ):
        s_d: int = self.get_param_value("sword_damage")
        b_d: int = self.get_param_value("bow_damage")
        c_d: int = self.get_param_value("catapult_damage")
        return s_d*swords+b_d*bows+c_d*catapults



defaultSolver = PizzasTantricasSolver
