from telegram import Update
from telegram.ext import CallbackContext

def handleExceptions(function):
    def insideFunc(update : Update, context : CallbackContext):
        try:
            function(update, context)
        except Exception as e :
            update.message.reply_text("Error no controlado en la función: "+function.__name__+" 😅 \n\n "+str(e))
            print("Error no controlado en la función: ",function.__name__)
            print(e)
   
    return insideFunc

def handleUnderConstruction(function):
    def insideFunc(update : Update, context : CallbackContext):
        update.message.reply_text("Esta funcionalidad esta en pruebas. Usala bajo tu propio riesgo 😅.")
        function(update, context)
    return insideFunc
