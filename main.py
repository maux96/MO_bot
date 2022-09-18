#!../env/bin/python3
from os import environ
from json import dumps

from telegram import CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, MessageHandler , Filters

from exception_handler import handleExceptions, handleUnderConstruction, handleSpam 
from solvers.dynamic_load import enumerate_solvers, get_solver_info
from utils import get_veredict

from typing import Tuple, List, Dict, TypedDict

TOKEN = environ["TOKEN"]

ID_PREFIX = "/i__"
GEN_JSON_PREFIX = "GEN_JSON_PREFIX_"
GEN_JSON_SPECIFIC_PREFIX = "GEN_JSON_SPECIFIC_PREFIX_"



def main():
    

    updater = Updater(token=TOKEN, workers=8)
    dp = updater.dispatcher
    
    # handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("identify", identify_student))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("enum", enumerate_problems_id,run_async=True))

    dp.add_handler(MessageHandler(Filters.regex('^'+ID_PREFIX),callback=solver_info,run_async=True))
    
    dp.add_handler(MessageHandler(Filters.document, send_solution, run_async=True)) 
    dp.add_handler(MessageHandler(Filters.text, send_solution_in_message, run_async=True))

    dp.add_handler(CallbackQueryHandler(pattern="^"+GEN_JSON_PREFIX,callback=button_gen_json, run_async=True))
    dp.add_handler(CallbackQueryHandler(pattern="^"+GEN_JSON_SPECIFIC_PREFIX,callback=button_gen_specific_json, run_async=True))

    updater.start_polling()
    updater.idle()

@handleExceptions
def start(update : Update, context : CallbackContext):
    id = update.message.from_user.id 

    update.message.reply_text("Hola, bienvenido al bot de la asignatura de Modelos de Optimización 🤗🤗🤗.")
    help(update,context)


    pass

@handleExceptions
@handleSpam
def send_solution(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
     
    mess = update.message.reply_text("...estamos trabajando...")

    solution = update.message.document.get_file().download_as_bytearray()
    solution = str(solution,"utf8")

    veredict = get_veredict(solution)

    mess.edit_text(veredict)

    pass    


@handleExceptions
@handleSpam
def send_solution_in_message(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
    
    mess = update.message.reply_text("...estamos trabajando...")

    solution = update.message.text

    veredict = get_veredict(solution)

    mess.edit_text(veredict)
    pass

@handleExceptions
@handleUnderConstruction
def identify_student(update : Update, context : CallbackContext):
    id = update.message.from_user.id 

    name, group = context.args[:2] 

    print("Se autentico el usuario", name, "del grupo", group)
    update.message.reply_text("Hola "+ name+ ", gracias por autenticarte 🤗.")
    pass

@handleExceptions
@handleSpam
def enumerate_problems_id(update : Update, context : CallbackContext):
    
    s = "Solvers disponibles: \n\n- "
    update.message.reply_text(s + "\n- ".join(enumerate_solvers(id_prefix=ID_PREFIX)))


@handleExceptions
def solver_info(update : Update, context : CallbackContext):
    solver_id = update.message.text[len(ID_PREFIX):]
    solver_info=get_solver_info(solver_id)
    solver_info = f'{solver_info["title"]}\n(id: {solver_info["id"]})\n\n {solver_info["text"]} \n\nVariables necesarias:\n -' + '\n -'.join([ var["name"]+" : "+var["text"] for var in  solver_info['used_vars']])

    buttons = [
        [InlineKeyboardButton("Generar JSON de respuesta",callback_data=GEN_JSON_PREFIX+solver_id)],
        [InlineKeyboardButton("Generar JSON de respuesta específico ",callback_data=GEN_JSON_SPECIFIC_PREFIX+solver_id)],
    ]
    update.message.reply_text(solver_info,reply_markup=InlineKeyboardMarkup(buttons))
    
    update.message.delete()


# posible bug si sucede un error dentro de esta funcion con el tema del update.message (no existe) :(
@handleExceptions
def button_gen_json(update : Update, context : CallbackContext):
    q = update.callback_query
      
    solver_id=q["data"][len(GEN_JSON_PREFIX):]
    solver_info=get_solver_info(solver_id)

    #construimos el JSON
    json = dumps({
        "_id": solver_id,
        "_values":{
            v["name"]:"TU_SOLUCION"  for v in solver_info["used_vars"]
        }
    })
     
    mess = "Para el problema `"+ solver_id +"` crea un json parecido a este y mandalo con tu solucion (puedes mandarla en un mensaje normal de Telegram 😉 )"
    mess+= "\n\n`"+json+"`\n\n"
    mess+= 'Sustituye `"TU_SOLUCION"` (quita las comillas 😅) por el valor asociado a cada variable. 🙆'
    q.from_user.send_message(mess,"Markdown")

def button_gen_specific_json(update : Update, context : CallbackContext):
    q = update.callback_query

    solver_id=q["data"][len(GEN_JSON_SPECIFIC_PREFIX):]

    solver_info=get_solver_info(solver_id)
        
    #construimos el JSON
    json = dumps({
        "_id": solver_id,
        "_values":{
            v["name"]:"TU_SOLUCION"  for v in solver_info["used_vars"]
        },
        "_parameters":{
            v["name"]:"TU_PARAMETRO"  for v in solver_info["used_params"]
        }
    })
    
    mess = "Para el problema `"+ solver_id +"` crea un json parecido a este y mandalo con tu solucion (puedes mandarla en un mensaje normal de Telegram 😉 )"
    mess+= "\n\n`"+json+"`\n\n"
    mess+= 'Sustituye `"TU_SOLUCION"` (quita las comillas 😅) por el valor asociado a cada variable. 🙆\n'
    mess+= 'Sustituye `"TU_PARAMETRO"` (quita las comillas 😅) por el valor asociado a cada parámetro. 🙆'

    new_message=q.from_user.send_message(mess,"Markdown")

    mess=f"Descripcion de parametros ({solver_id}):\n\n"
    for v in solver_info["used_params"]:
        mess+=" -"+ v['name']+" : "+ v["text"] + "\n"   # problema con esto para el Markdown :(
    mess+= "\n"

    new_message.reply_text(mess)




@handleExceptions
def help(update : Update, context : CallbackContext):
    message=""
    message="Para conocer los solvers disponibles usa /enum.\n"
    message+="Puedes mandar las soluciones en un `*.json`. Este tiene que tener el formato:\n\n"
    message+="""
    `
    {
        "_id":"<id_del_problema>",

        "_values": {
            "var1": value1,
            "var2": value2,
                .
                .
                .
            "varN": valueN
        },
        "_parameters:"{
            "param1": valuep1,
            "param2": valuep2,
                .
                .
                .
            "paramN": valuepN,
        }
    }
    `
    """
    message+="\n\n Siendo `_id` el identificador del problema y `valueI` el valor que considera el estudiante que es el correcto para una varible con nombre `varI`."
    message+="\n No es necesario mandar el campo `_parameters`, en caso de no mandarse se asumen los parametros por defecto del problema."
    message+="\n\nEl control de errores que hay implementado es muuuuuy simple, asi q suave plis 😓...."
    update.message.reply_text(message,"Markdown")
    pass


if __name__=="__main__":
    print("Starting the MO bot...")
    main()

