from gekko.gekko import GKVariable
from BaseSolver import BaseSolver
from typing import Dict, Any 
from gekko import GEKKO


class GotSolver(BaseSolver):
    def _set_default_info(self):
        self._name="got1"
        self._title="Game Of Thrones I"
        self._text="""Casa Mormont

Necesitamos que le diga a los jefes de la casa que cantidad de espadas, arcos y catapultas deben fabricar.
Necesitamos realizar el mayor daño posible a las tropas enemigas para alcanzar la victoria.
Las espadas se rompen al realizar 15 de daño, los arcos al realizar 10 y las catapultas al realizar 80.
Las catapultas no hacen daño en área (menuda estafa de sistema).
        """
    def _set_default_params_and_variables(self):
        self._default_parameters = {
            "hierro":(600000,"Cantidad de Hierro"),
            "madera":(400000,"Cantidad de Madera"),
            "cuero":(800000,"Cantidad de Cuero"),

            "c_h_sword":(10,"Costo de hierro de las espadas"),
            "c_m_sword":(2, "Costo de madera de las espadas"),
            "c_c_sword":(4, "Costo de cuero de las espadas"),

            "c_h_bow":(2, "Costo de hierro de los arcos"),
            "c_m_bow":(10,"Costo de madera de los arcos"),
            "c_c_bow":(5, "Costo de cuero de los arcos "),

            "c_h_catapult":(30, "Costo de hierro de las catapultas"),
            "c_m_catapult":(100,"Costo de madera de las catapultas"),
            "c_c_catapult":(50, "Costo de cuero de las catapultas "),


            "sword_damage":(15,"Daño de las espadas"),
            "bow_damage":(10,"Daño de los arcos"),
            "catapult_damage":(8,"Daño de las catapultas")
        }
        self._variables_descriptions= {
            "amount_swords":"Cantidad de espadas.",
            "amount_bows":"Cantidad de arcos.",
            "amount_catapults":"Cantidad de catapultas."
        }


    def _solve_model(self):

        m = GEKKO(remote=False) #Initialize gekko

        m.options.SOLVER = 1 # ??

        iron_units = m.Param(value=self.get_param_value("hierro") )
        wood_units = m.Param(value=self.get_param_value("madera") )
        leather_units = m.Param(value=self.get_param_value("cuero") )

        amount_swords    = m.Var(lb = 0,integer=True)
        amount_bows      = m.Var(lb = 0,integer=True)
        amount_catapults = m.Var(lb = 0,integer=True)

        #costos
        c_h_sword = self.get_param_value("c_h_sword") 
        c_m_sword = self.get_param_value("c_m_sword") 
        c_c_sword = self.get_param_value("c_c_sword") 
        
        c_h_bow = self.get_param_value("c_h_bow") 
        c_m_bow = self.get_param_value("c_m_bow") 
        c_c_bow = self.get_param_value("c_c_bow") 

        c_h_catapult = self.get_param_value("c_h_catapult") 
        c_m_catapult = self.get_param_value("c_m_catapult") 
        c_c_catapult = self.get_param_value("c_c_catapult") 


        m.Equation(amount_swords*c_h_sword+amount_bows*c_h_bow+amount_catapults*c_h_catapult<=iron_units) #Iron
        m.Equation(amount_swords*c_m_sword+amount_bows*c_m_bow+amount_catapults*c_m_catapult<=wood_units) #Wood
        m.Equation(amount_swords*c_c_sword+amount_bows*c_c_bow+amount_catapults*c_c_catapult<=leather_units) #Leather

        m.Maximize(self.total_damage(amount_swords,amount_bows,amount_catapults))

        m.solve(disp = False)

        return {
            "amount_swords": amount_swords.VALUE[0],
            "amount_bows": amount_bows.VALUE[0],
            "amount_catapults": amount_catapults.VALUE[0],
            "obj": self.total_damage(amount_swords.VALUE[0],amount_bows.VALUE[0],amount_catapults.VALUE[0])
        }

    def _compare_solution(self, solution: Dict[str, Any]):
        
        #totales
        t_hierro=self.get_param_value("hierro") 
        t_madera=self.get_param_value("madera") 
        t_cuero=self.get_param_value("cuero") 

        #costos
        c_h_sword = self.get_param_value("c_h_sword") 
        c_m_sword = self.get_param_value("c_m_sword") 
        c_c_sword = self.get_param_value("c_c_sword") 
        
        c_h_bow = self.get_param_value("c_h_bow") 
        c_m_bow = self.get_param_value("c_m_bow") 
        c_c_bow = self.get_param_value("c_c_bow") 

        c_h_catapult = self.get_param_value("c_h_catapult") 
        c_m_catapult = self.get_param_value("c_m_catapult") 
        c_c_catapult = self.get_param_value("c_c_catapult") 

        #mensajes de error personalizados por si no alcanzan los materiales :(
        sword = solution["amount_swords"]
        t_hierro -= sword*c_h_sword
        t_madera -= sword*c_m_sword
        t_cuero -= sword*c_c_sword
        if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
            self._log_message("No se pueden construir tantas espadas :(")
            return

        bow = solution["amount_bows"]
        t_hierro -= bow*c_h_bow
        t_madera -= bow*c_m_bow
        t_cuero -=  bow*c_c_bow
        if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
            self._log_error("No se pueden construir tantos arcos :(")
            return

        catapult = solution["amount_catapults"]
        t_hierro -= catapult*c_h_catapult
        t_madera -= catapult*c_m_catapult
        t_cuero -=  catapult*c_c_catapult
        if t_hierro < 0 or t_madera < 0 or t_cuero < 0:
            self._log_error("No se pueden construir tantas catapultas :(")
            return

        if(sword < 0 or bow < 0 or catapult < 0):
            self._log_error('Has creado una cantidad negativa, el mundo implosiona, mision cumplida, los caminantes blancos han muerto')
            return
         
        #calculo de danno 
        damage_dealt =self.total_damage(sword,bow,catapult)
        best_posible =solution["obj"]
        self._log_message(f'Hemos realizado {damage_dealt} daños en las tropas enemigas')
        if damage_dealt < best_posible*0.98:
           self._log_message(f'Necesitamos {best_posible*0.98 - damage_dealt} de daño para alcanzar la victoria')
        if(damage_dealt > best_posible*0.98):
           self._log_message('Hemos aniquilado a las tropas enemigas, una rotunda victoria')
        elif(damage_dealt > best_posible*0.8):
           self._log_message('Estuvimos tan cerca de la victoria, fue un honor luchar a su lado')
        elif(damage_dealt > best_posible*0.5):
           self._log_message('Al menos eliminamos la mitad de sus tropas')
        elif(damage_dealt < best_posible*0.1):
           self._log_message('No se como alguien logró hacerlo tan mal')
        else:
           self._log_message('Que desastre!')


    def total_damage(self, swords: int | GKVariable, bows: int | GKVariable, catapults: int | GKVariable ):
        s_d: int = self.get_param_value("sword_damage")
        b_d: int = self.get_param_value("bow_damage")
        c_d: int = self.get_param_value("catapult_damage")
        return s_d*swords+b_d*bows+c_d*catapults



defaultSolver = GotSolver
