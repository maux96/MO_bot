from typing import List

from asyncio.unix_events import BaseChildWatcher
from telegram.ext import BaseHandler, CommandHandler
from telegram.ext._utils.types import HandlerCallback


_listHandler: List[BaseHandler]  = []
def get_exported():
    return _listHandler

def export(handler_type, *args):
    """ Decorador para marcar como usable un manejador en el bot """
    def _inner_function(handler: HandlerCallback):
        _listHandler.append(handler_type(*args, callback=handler))
        return handler 
    return _inner_function 


