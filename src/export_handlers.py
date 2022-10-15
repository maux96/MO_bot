from typing import List

from telegram.ext import BaseHandler 
from telegram.ext._utils.types import HandlerCallback


_listHandler: List[BaseHandler]  = []
def get_exported():
    return _listHandler

def export(handler_type, *args,**named_args):
    """ Decorador para marcar como usable un handler en el bot """
    def _inner_function(handler: HandlerCallback):
        _listHandler.append(handler_type(*args, **named_args,callback=handler))
        return handler 
    return _inner_function 


