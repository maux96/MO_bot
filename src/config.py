from os import environ
from local_provider import LocalSolverProvider

""" Telegram Bot Token """
TOKEN = environ["TOKEN"]

""" Solver Provider """
solver_provider = LocalSolverProvider()


