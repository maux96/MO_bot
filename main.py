#!../env/bin/python3
from os import environ

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler , Filters

from exception_handler import handleExceptions, handleUnderConstruction

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

    update.message.reply_text("Subiste esto :\n"+solution)
    #
    # Registrar 'solution' como la solucion asociada a un problema definido por el usuario :D
    #

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
def help(update : Update, context : CallbackContext):

    message="- Primero debes autenticarte usando el comando\n"
    message+="  /identify <nombre> <grupo>\n"
    message+="  Usa un nombre que te identifique solo a ti en tu grupo y que no contenga espacios.\n\n"  
    message+="- Luego puedes mandar las soluciones a en un *.txt, la primera linea debe tener el formato.\n"
    message+="  # <id_del_problema> ..."

    update.message.reply_text(message)
    pass


if __name__=="__main__":
    print("Starting the MO bot...")
    main()

