#!../env/bin/python3
from os import environ

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler , Filters

from exception_handler import handleExceptions, handleUnderConstruction
from solvers.dynamic_load import verify_solution 

TOKEN = environ["TOKEN"]

def main():
    

    updater = Updater(token=TOKEN, workers=8)
    dp = updater.dispatcher
    
    # handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("identify", identify_student))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.document, send_solution, run_async=True))

    updater.start_polling()
    updater.idle()

@handleExceptions
def start(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
    
    update.message.reply_text("Hola, bienvenido al bot de la asignatura de Modelos de Optimización 🤗🤗🤗.")
    help(update,context)
   

    pass

@handleExceptions
@handleUnderConstruction
def send_solution(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
     
    solution = update.message.document.get_file().download_as_bytearray()
    solution = str(solution,"utf8")

    errors, messages=verify_solution(solution)
     
    mess = update.message.reply_text("...estamos trabajando...")

    if errors:
        mess.edit_text("Errores 😓\n\n"+ "\n-".join(errors))
    elif  messages:
        mess.edit_text("Resultados 🤔\n\n"+ "\n-".join(messages))
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
@handleUnderConstruction
def enumerate_problems_id(update : Update, context : CallbackContext):
    raise Exception("NotImplementedException!")
    pass

@handleExceptions
def help(update : Update, context : CallbackContext):
    message=""
    #message="- Primero debes autenticarte usando el comando\n"
    #message+="  /identify <nombre> <grupo>\n"
   # message+="  Usa un nombre que te identifique solo a ti en tu grupo y que no contenga espacios.\n\n"  
    message+="Puedes mandar las soluciones a en un `*.json`. Este tiene que tener el formato:\n\n"
    message+="""
    `{
        "_id":"<id_del_problema>",
        "_values":{
            "var1": value1,
            "var2": value2,

            "varN": valueN
        }
     }`
    """
    message+="\n\n Siendo `_id` el identificador del problema y `valuei` el valor que considera el estudiante que es el correcto para una varible con nombre `vari`."

    update.message.reply_text(message)
    pass


if __name__=="__main__":
    print("Starting the MO bot...")
    main()

