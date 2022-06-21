from telegram import Update
from telegram.ext import CallbackContext
from time import time

_DEV = False #activar para tener mas precision con los errores, si ocurre un error se detiene la app :D

def handleExceptions(function):
    def insideFunc(update : Update, context : CallbackContext):
        try:
            function(update, context)
        except Exception as e :
            update.message.reply_text("Error no controlado en la función: "+function.__name__+" 😅 \n\n "+str(e))
            print("Error no controlado en la función: ",function.__name__)
            print(e)
            _restore_vars(update.message.from_user.id)
            
    if _DEV:
    	return function 

    return insideFunc

def handleUnderConstruction(function):
    def insideFunc(update : Update, context : CallbackContext):
        update.message.reply_text("Esta funcionalidad esta en pruebas. Usala bajo tu propio riesgo 😅.")
        function(update, context)
    return insideFunc



# la ultima vez (SPAM_DICT[0]) que el usuario uso una funcion critica para el spam  y si la esta usando (SPAM_DICT[1])
SPAM_DICT : dict[int : (float,bool)] ={ }
TIME_SPACE = 5
def handleSpam(function):
    def insideFunc(update : Update, context : CallbackContext):
        id = update.message.from_user.id
        
        if SPAM_DICT.__contains__(id) and ( SPAM_DICT[id][1] or (time() - SPAM_DICT[id][0] < TIME_SPACE )):
            update.message.reply_text("Ehh, cual es el spam 🤨??... vamo a calmarno 🐢")
        else:
            SPAM_DICT[id]= -1, True
            function(update, context)
            SPAM_DICT[id]= time(), False

    return insideFunc

def _restore_vars(id):
    if SPAM_DICT.__contains__(id):
        SPAM_DICT[id]= time(), False 




