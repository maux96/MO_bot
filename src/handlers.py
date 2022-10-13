from typing import Tuple, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler 
from telegram.ext import filters
from telegram.ext import ContextTypes

from some_utils import get_exported, export
from dynamic_loader import get_solver_info 


def get_handlers():
    return get_exported()


@export(CommandHandler,"start")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Simple bot response """
    if update.effective_user:
        user_name = update.effective_user.first_name
    else:
        raise Exception("User Not Identified :(")
    await update.message.reply_text(f"Hola {user_name}!\n\n Bienvenido al bot de la asignatura Modelos de Optimizacion.")

@export(CommandHandler,"help")
async def help_handler(update: Update, context: CallbackContext):
    """ Displays help """
    await update.message.reply_text("Imprimir ayuda!")


@export(MessageHandler,filters.Document.ALL)
async def document_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("un documento!!")
    pass


@export(MessageHandler, filters.Text())
async def execute_python_line(update: Update, context: CallbackContext):
    await update.message.reply_text(f"solution:\n  {eval(update.message.text)}")
     

ID_PREFIX = "/i__"
GEN_JSON_PREFIX = "GEN_JSON_PREFIX_"
GEN_JSON_SPECIFIC_PREFIX = "GEN_JSON_SPECIFIC_PREFIX_"


@export(MessageHandler, filters.Regex(f"^{ID_PREFIX}"))
async def solver_info(update : Update, context : CallbackContext):
    solver_name = update.message.text[len(ID_PREFIX):]
    solver_info=get_solver_info(solver_name)
    solver_info = f'{solver_info["title"]}\n\
        (id: {solver_info["id"]})\n\n\
        {solver_info["text"]} \n\n\
        Variables necesarias:\n\
        -' + '\n -'.join([ var["name"]+" : "+var["text"]
        for var in  solver_info['used_vars']])
    #
    buttons = [
        [InlineKeyboardButton("Generar JSON de respuesta",callback_data=GEN_JSON_PREFIX+solver_name)],
        [InlineKeyboardButton("Generar JSON de respuesta específico ",callback_data=GEN_JSON_SPECIFIC_PREFIX+solver_name)],
    ]
    await update.message.reply_text(solver_info,reply_markup=InlineKeyboardMarkup(buttons))
    await update.message.delete()
