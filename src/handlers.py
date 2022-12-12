from typing import List, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, MessageHandler 
from telegram.ext import filters
from telegram.ext import ContextTypes
from BaseSolver import UserSolution

from export_handlers import get_exported, export
from config import solver_provider 

import json 
from json_formating import json_stringify


def get_handlers():
    return get_exported()


cached_data: Dict[str,Any] = {}

@export(CommandHandler,"start")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Simple bot response """
    if update.effective_user:
        user_name = update.effective_user.first_name
    else:
        raise Exception("User Not Identified :(")
    await update.message.reply_text(f"Hola {user_name}!\n\n Bienvenido al bot de la asignatura Modelos de Optimizacion.\n\n\nPara mas info -> /help")

@export(CommandHandler,"help")
async def help_handler(update: Update, context: CallbackContext):
    """ Displays help """
    message="Para conocer los solvers disponibles usa /enum.\n"
    message+="Puedes mandar las soluciones en un `*.json`. Este tiene que tener el formato:\n\n"
    message+="""
    `
    {
        "id":"<id_del_problema>",
        "values": {
            "var1": value1,
            "var2": value2,
                .
                .
                .
            "varN": valueN
        },
        "parameters:"{
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
    message+="\n\n Siendo `id` el identificador del problema y `valueI` el valor que considera el estudiante que es el correcto para una varible con nombre `varI`."
    message+="\n En el caso de mandar el campo `parameters:null` se asumen los parametros por defecto del problema."
    message+="\n\nEl control de errores que hay implementado es muuuuuy simple, asi q suave plis 😓...."

    await update.message.reply_text(message,"Markdown")        


@export(CommandHandler, "enum")
async def enumerate_solvers(update: Update, context: CallbackContext):
    """ Enumera todos los solvers disponibles """

    mess = await update.message.reply_text("...estamos trabajando...")


    if "enumerated_solvers" in cached_data:
        solvers: List[str] = cached_data["enumerated_solvers"]
    else:
        solvers_available = solver_provider.enumerate_available() 
        solvers = [
            f"{title} (id: {ID_PREFIX}{name})" for title, name in solvers_available
        ] 
        cached_data["enumerated_solvers"] = solvers

    await mess.edit_text(
        "AvailableSolvers:\n\n- "+"\n- ".join(solvers))
     

ID_PREFIX = "/I__"
GEN_JSON_PREFIX = "GEN_JSON_PREFIX_"
GEN_JSON_SPECIFIC_PREFIX = "GEN_JSON_SPECIFIC_PREFIX_"

@export(MessageHandler, filters.Regex(f"^{ID_PREFIX}"))
async def solver_info(update : Update, context : CallbackContext):

    mess = await update.message.reply_text("...estamos trabajando...")

    solver_name = update.message.text[len(ID_PREFIX):]
    solver_info = solver_provider.get_solver_info(solver_name)
    solver_end_string  = solver_info["title"]
    solver_end_string += "  (name:"+ solver_info["name"]+")\n\n"
    solver_end_string += solver_info["description"]+"\n\n"
    solver_end_string += "Variables necesarias:\n"
    solver_end_string += '- ' + '\n- '.join([
        f"{name}: {desc}" for name,(desc,_) in solver_info['variables'].items()
    ])

    buttons = [
        [InlineKeyboardButton("Generar JSON de respuesta",
                    callback_data=GEN_JSON_PREFIX+solver_name)],
        [InlineKeyboardButton("Generar JSON de respuesta específico ",
                    callback_data=GEN_JSON_SPECIFIC_PREFIX+solver_name)],
    ]
    await mess.edit_text(solver_end_string,
                            reply_markup=InlineKeyboardMarkup(buttons))
    await update.message.delete()

@export(CallbackQueryHandler, pattern=f"^{GEN_JSON_PREFIX}")
async def generate_json_for_solver(update: Update, context: CallbackContext):
    q = update.callback_query

    solver_id=q.data[len(GEN_JSON_PREFIX):]
    solver_info=solver_provider.get_solver_info(solver_id)

    #construimos el JSON
    builded_json = json_stringify({
        "id": '"'+solver_id+'"',
        "values":{
            name:(solver_info["variables"][name][1]
                  if solver_info["variables"][name][1]!=None
                  else "TU_SOLUCION")
            for name in solver_info["variables"]
        },
        "parameters":"null"
    })
     
    mess = "Para el problema `"+ solver_id +"` crea un json parecido a este y\
    mandalo con tu solucion\
    (puedes mandarla en un mensaje normal de Telegram 😉 )"
    
    mess+= "\n\n`"+builded_json+"`\n\n"
    mess+= 'Sustituye `"TU_SOLUCION"` (quita las comillas 😅) por el valor\
    asociado a cada variable. 🙆'

    await q.from_user.send_message(mess,"Markdown")


@export(CallbackQueryHandler, pattern=f"^{GEN_JSON_SPECIFIC_PREFIX}")
async def generate_specific_json_for_solver(update: Update,
                                            context: CallbackContext):
    q = update.callback_query

    solver_id=q.data[len(GEN_JSON_SPECIFIC_PREFIX):]
    solver_info=solver_provider.get_solver_info(solver_id)


    #construimos el JSON
    builded_json = json_stringify({
        "id": '"'+solver_id+'"',
        "values":{
            name:"TU_SOLUCION"  for name in solver_info["variables"]
        },
        "parameters":{
            name:"TU_PARAM"  for name in solver_info["parameters"]
        }
    })
     
    mess = "Para el problema `"+ solver_id +"` crea un json parecido a este y\
    mandalo con tu solucion\
    (puedes mandarla en un mensaje normal de Telegram 😉 )"

    mess+= "\n\n`"+builded_json+"`\n\n"
    mess+= 'Sustituye `"TU_SOLUCION"` (quita las comillas 😅) por el valor\
    asociado a cada variable. 🙆'

    mess+= 'Sustituye `"TU_PARAM"` (quita las comillas 😅) por el valor \
    asociado a cada parámetro. 🙆'

    mess+= '\n\n Parametros:\n- '
    mess+= "\n- ".join(
        [ f"`{name}`: {info}"
            for name,(_,info) in solver_info["parameters"].items()
        ])

    await q.from_user.send_message(mess,"Markdown")



@export(MessageHandler,filters.TEXT & filters.Regex(r'^{'))
async def compare_solution_handler(update: Update, context: CallbackContext):
    mess = await update.message.reply_text("...estamos trabajando...")

    veredict = get_veredict(update.message.text)
    await mess.edit_text(veredict)

@export(MessageHandler,filters.Document.ALL)
async def compare_document_solution(update: Update, context: CallbackContext):
    mess = await update.message.reply_text("...estamos trabajando...")

    solution =  await (await update.message.document.get_file()).download_as_bytearray()
    solution = str(solution,"utf8")

    veredict = get_veredict(solution)
    await mess.edit_text(veredict)


def get_veredict(solution: str):
    user_solution: UserSolution =json.loads(solution) 
    solver_name :str=user_solution["id"]
    messages, errors = solver_provider.compare_solution(solver_name,user_solution)

    if errors:
        return ("Errores 😓:\n\n-"+ "\n-".join(errors))
    elif messages:
        return ("Resultados 🤔:\n\n-"+ "\n-".join(messages))
    else: 
        return ("No hay nada que mostrar 😅.... de quién será la culpa 😒... ")
 
