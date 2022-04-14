#!../env/bin/python3
from os import environ
from json import dumps

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, MessageHandler , Filters

from exception_handler import handleExceptions, handleUnderConstruction
from solvers.dynamic_load import verify_solution, enumerate_solvers, get_solver_info

TOKEN = environ["TOKEN"]

ID_PREFIX = "/i__"
GEN_JSON_PREFIX = "GEN_JSON_"

def main():
    

    updater = Updater(token=TOKEN, workers=8)
    dp = updater.dispatcher
    
    # handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("identify", identify_student))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("enum", enumerate_problems_id))

    dp.add_handler(MessageHandler(Filters.regex('^'+ID_PREFIX),callback=solver_info))
    
    dp.add_handler(MessageHandler(Filters.document, send_solution, run_async=True))
    dp.add_handler(CallbackQueryHandler(pattern="^"+GEN_JSON_PREFIX,callback=button_gen_json))

    updater.start_polling()
    updater.idle()

@handleExceptions
def start(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
    
    update.message.reply_text("Hola, bienvenido al bot de la asignatura de Modelos de Optimización 🤗🤗🤗.")
    help(update,context)
   

    pass

@handleExceptions
def send_solution(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
     
    solution = update.message.document.get_file().download_as_bytearray()
    solution = str(solution,"utf8")

    errors, messages=verify_solution(solution)
     
    mess = update.message.reply_text("...estamos trabajando...")

    if errors:
        mess.edit_text("Errores 😓:\n\n-"+ "\n-".join(errors))
    elif  messages:
        mess.edit_text("Resultados 🤔:\n\n-"+ "\n-".join(messages))
    else: 
        mess.edit_text("No hay nada que mostrar 😅.... de quién será la culpa 😒... ")
    
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
def enumerate_problems_id(update : Update, context : CallbackContext):
    
    s = "Solvers disponibles: \n\n- "
    update.message.reply_text(s + "\n- ".join(enumerate_solvers(id_prefix=ID_PREFIX)))


@handleExceptions
def solver_info(update : Update, context : CallbackContext):
    solver_id = update.message.text[len(ID_PREFIX):]
    solver_info=get_solver_info(solver_id)
    solver_info = f'{solver_info["title"]}\n(id: {solver_info["id"]})\n\n {solver_info["text"]} \n\nVariables necesarias:\n -' + '\n -'.join([ var["name"]+" : "+var["text"] for var in  solver_info['used_vars']])

    buttons = [[InlineKeyboardButton("Generar JSON de respuesta",callback_data=GEN_JSON_PREFIX+solver_id)]]
    update.message.reply_text(solver_info,reply_markup=InlineKeyboardMarkup(buttons))
    
    update.message.delete()


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
    
    mess = "Para el problema `"+ solver_id +"` crea un json parecido a este y mandalo con tu solucion"
    mess+= "\n\n`"+json+"`\n\n"
    mess+= 'Sustituye `"TU_SOLUCION"` por el valor asociado a cada variable. 🙆'
    q.from_user.send_message(mess,"Markdown")


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
        }
    }
    `
    """
    message+="\n\n Siendo `_id` el identificador del problema y `valuei` el valor que considera el estudiante que es el correcto para una varible con nombre `vari`."

    update.message.reply_text(message,"Markdown")
    pass


if __name__=="__main__":
    print("Starting the MO bot...")
    main()

