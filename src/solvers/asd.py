from gekko.gekko import GKVariable
from BaseSolver import BaseSolver
from typing import Dict, Any, Literal
from gekko import GEKKO


class GotSolver(BaseSolver):
    def _set_default_info(self):
        self._title="Game Of Thrones I"
        self._text="""Casa Mormont

Necesitamos que le diga a los jefes de la casa que cantidad de espadas, arcos y catapultas deben fabricar.
Necesitamos realizar el mayor daño posible a las tropas enemigas para alcanzar la victoria.
Las espadas se rompen al realizar 15 de daño, los arcos al realizar 10 y las catapultas al realizar 80.
Las catapultas no hacen daño en área (menuda estafa de sistema).
        """
    def _set_default_params(self):
        self._default_parameters = {
            "hierro":600000,
            "madera":400000,
            "cuero":800000,

            "c_h_sword":10,
            "c_m_sword":2,
            "c_c_sword":4,

            "c_h_bow":2,
            "c_m_bow":10,
            "c_c_bow":5,

            "c_h_catapult":30,
            "c_m_catapult":100,
            "c_c_catapult":50,


            "sword_damage":15,
            "bow_damage":10,
            "catapult_damage":80
        }

    def _solve_model(self):

        m = GEKKO(remote=False) #Initialize gekko

        m.options.SOLVER = 1 # ??

        iron_units = m.Param(value=self.GetParamValue("hierro") )
        wood_units = m.Param(value=self.GetParamValue("madera") )
        leather_units = m.Param(value=self.GetParamValue("cuero") )

        amount_swords    = m.Var(lb = 0,integer=True)
        amount_bows      = m.Var(lb = 0,integer=True)
        amount_catapults = m.Var(lb = 0,integer=True)

        #costos
        c_h_sword = self.GetParamValue("c_h_sword") 
        c_m_sword = self.GetParamValue("c_m_sword") 
        c_c_sword = self.GetParamValue("c_c_sword") 
        
        c_h_bow = self.GetParamValue("c_h_bow") 
        c_m_bow = self.GetParamValue("c_m_bow") 
        c_c_bow = self.GetParamValue("c_c_bow") 

        c_h_catapult = self.GetParamValue("c_h_catapult") 
        c_m_catapult = self.GetParamValue("c_m_catapult") 
        c_c_catapult = self.GetParamValue("c_c_catapult") 


        m.Equation(amount_swords*c_h_sword+amount_bows*c_h_bow+amount_catapults*c_h_catapult<=iron_units) #Iron
        m.Equation(amount_swords*c_m_sword+amount_bows*c_m_bow+amount_catapults*c_m_catapult<=wood_units) #Wood
        m.Equation(amount_swords*c_c_sword+amount_bows*c_c_bow+amount_catapults*c_c_catapult<=leather_units) #Leather

        m.Maximize(total_damage(amount_swords,amount_bows,amount_catapults,self._default_parameters))

        m.solve(disp = False)

        return {
            "amount_swords": amount_swords.VALUE[0],
            "amount_bows": amount_bows.VALUE[0],
            "amount_catapults": amount_catapults.VALUE[0],
            "obj": total_damage(amount_swords.VALUE[0],amount_bows.VALUE[0],amount_catapults.VALUE[0],self._default_parameters)
        }

    def _compare_solution(self, solution: Dict[str, Any]):
        
        #totales
        t_hierro=self.GetParamValue("hierro") 
        t_madera=self.GetParamValue("madera") 
        t_cuero=self.GetParamValue("cuero") 

        #costos
        c_h_sword = self.GetParamValue("c_h_sword") 
        c_m_sword = self.GetParamValue("c_m_sword") 
        c_c_sword = self.GetParamValue("c_c_sword") 
        
        c_h_bow = self.GetParamValue("c_h_bow") 
        c_m_bow = self.GetParamValue("c_m_bow") 
        c_c_bow = self.GetParamValue("c_c_bow") 

        c_h_catapult = self.GetParamValue("c_h_catapult") 
        c_m_catapult = self.GetParamValue("c_m_catapult") 
        c_c_catapult = self.GetParamValue("c_c_catapult") 

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
        damage_dealt =total_damage(sword,bow,catapult,self._default_parameters)
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




def total_damage(swords: int | GKVariable,bows: int | GKVariable,catapults: int | GKVariable, model_params: Dict[str, Any]):
    s_d = model_params["sword_damage"]
    b_d = model_params["bow_damage"]
    c_d = model_params["catapult_damage"]
    return s_d*swords+b_d*bows+c_d*catapults



defaultSolver = GotSolver
