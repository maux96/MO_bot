from typing import Dict, Tuple, List
from telegram import Update
from telegram.ext import CallbackContext
from time import time

_DEV = False #activar para tener mas precision con los errores, si ocurre un error se detiene la app :D

def handleExceptions(function):
    def insideFunc(update : Update, context : CallbackContext):
        try:
            function(update, context)
        except Exception as e :
            #if update.message is None: return
            update.message.reply_text("Error no controlado en la función: "+function.__name__+" 😅 \n\n "+str(e))
            print("Error no controlado en la función: ",function.__name__)
            print(e)
            #if not update.message.from_user is None: 
            _restore_vars(update.message.from_user.id)
            
    if _DEV:
    	return function 

    return insideFunc

def handleUnderConstruction(function):
    def insideFunc(update : Update, context : CallbackContext):
        #if update.message is None:
        #    return
        update.message.reply_text("Esta funcionalidad esta en pruebas. Usala bajo tu propio riesgo 😅.")
        function(update, context)
    return insideFunc

#def handleType(typesToCheck: List[str]):
#    """ Esta funcion es lo que se me ocurrio para que el linter no me sacara ciertos errores de tipos :( """
#    def _insideFunc( func ):
#        def __insideFunc(update : Update, context : CallbackContext):
#            for ty in typesToCheck: 
#                if update.__getattribute__(ty) is None:
#                    return
#            func(update, context)
#        return __insideFunc
#    return _insideFunc


# la ultima vez (SPAM_DICT[0]) que el usuario uso una funcion critica para el spam  y si la esta usando (SPAM_DICT[1])
SPAM_DICT : Dict[int,Tuple[float,bool]] ={ }
TIME_SPACE = 5
def handleSpam(function):
    def insideFunc(update : Update, context : CallbackContext):
        #if update.message is None or update.message.from_user is None: return 
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




