from typing import Tuple, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler 
from telegram.ext import filters
from telegram.ext import ContextTypes

from some_utils import get_exported, export
from load_solvers import get_solver_info, enumerate_available


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


@export(CommandHandler, "enum")
async def enumerate_solvers(update: Update, context: CallbackContext):

    solvers = enumerate_available() 
    await update.message.reply_text("AvailableSolvers:\n\n- "+"\n- ".join(solvers))
     

ID_PREFIX = "/I__"
GEN_JSON_PREFIX = "GEN_JSON_PREFIX_"
GEN_JSON_SPECIFIC_PREFIX = "GEN_JSON_SPECIFIC_PREFIX_"

@export(MessageHandler, filters.Regex(f"^{ID_PREFIX}"))
async def solver_info(update : Update, context : CallbackContext):
    solver_name = update.message.text[len(ID_PREFIX):]
    solver_info = get_solver_info(solver_name)
    solver_end_string  = solver_info["title"]
    solver_end_string += "  (name:"+ solver_info["name"]+")\n\n"
    solver_end_string += solver_info["description"]+"\n\n"
    solver_end_string += "Variables necesarias:\n"
    solver_end_string += '- ' + '\n- '.join([
        f"{name}: {desc}" for name, desc in solver_info['variables'].items()
    ])

    buttons = [
        [InlineKeyboardButton("Generar JSON de respuesta",callback_data=GEN_JSON_PREFIX+solver_name)],
        [InlineKeyboardButton("Generar JSON de respuesta específico ",callback_data=GEN_JSON_SPECIFIC_PREFIX+solver_name)],
    ]
    await update.message.reply_text(solver_end_string,reply_markup=InlineKeyboardMarkup(buttons))
    await update.message.delete()
