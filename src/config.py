from os import environ, path
from github_provider import GithubProvider
from local_provider import LocalSolverProvider

""" Telegram Bot Token """
TOKEN = environ["TOKEN"]

""" Solver Provider """
solver_provider = LocalSolverProvider()


## Different provider
#solver_provider = GithubProvider(
#    user="maux96",
#    repo= "MO_bot",
#    branch="remake",
#    path_to_solvers="src/solvers"
#)


