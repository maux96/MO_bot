#!../env/bin/python3
from os import environ

from telegram.ext import Updater, CommandHandler, CallbackContext, MessegeHandler, Filters

from exception_handler import handleExceptions

TOKEN = environ["TOKEN"]

def main():

    updater = Updater(token=TOKEN, workers=8)
    dp = updater.dispatcher
    
    # handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("identify", identify_student))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessegeHandler(Filters.document, send_solution, run_async=True))


@handleExceptions
def start(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
    
    update.message.reply_text("Hola, bienvenido al bot de la asignatura de Modelos de Optimización 🤗🤗🤗.")
   

    pass

@handleExceptions
@handleUnderConstruction
def send_solution(update : Update, context : CallbackContext):
    id = update.message.from_user.id 
     
    pass

@handleExceptions
def identify_student(update : Update, context : CallbackContext):
    id = update.message.from_user.id 

    name, group = context.args[:2]

    print("Se autentico el usuario", name, "del grupo", group)
    update.message.reply_text("Hola", nombre, "gracias por autenticarte 🤗.")

    pass

@handleExceptions
@handleUnderConstruction
def help(update : Update, context : CallbackContext):

    message = """
    Primero debes autenticarte usando el comando
    /auth <nombre> <grupo>
    Usa un nombre que te identifique solo a ti en tu grupo y que no contenga espacios.  

    Luego puedes mandar las soluciones a en un *.txt, la primera linea debe tener el formato
    # <id_del_problema> ...  
    """
    update.message.reply_text(message)
    pass
