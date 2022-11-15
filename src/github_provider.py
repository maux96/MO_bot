
from typing import Tuple, List, Dict

import requests
from importlib.util import module_from_spec, spec_from_loader 
from os import listdir
from pathlib import Path

from BaseProvider import BaseProvider
from BaseSolver import SolverInfo, UserSolution, BaseSolver

class GithubProvider(BaseProvider):
    def __init__(self,*, user: str, repo: str, branch: str, path_to_solvers: str) -> None:
        self.user=user 
        self.repo=repo 
        self.branch=branch 
        self.path_to_solvers=path_to_solvers 

    @property
    def base_github_url_solvers(self):
        return f"https://api.github.com/repos/{self.user}/{self.repo}/contents/{self.path_to_solvers}/"

    @property
    def base_github_url_content(self):
        return f"https://raw.githubusercontent.com/{self.user}/{self.repo}/{self.branch}/"
         

    def get_solver(self, solver_name: str) -> BaseSolver:

        source=requests.get(self.base_github_url_content+f"{self.path_to_solvers}/{solver_name}.py").text

        spec = spec_from_loader(solver_name,loader=None)
        
        if spec == None:
            raise Exception("Solutioner not founded :(")

        module = module_from_spec(spec) 
        exec(source, module.__dict__)
        return module.defaultSolver()


    def compare_solution(self, solver_name: str, user_solution: UserSolution) -> Tuple[List[str], List[str]]:
        return self.get_solver(solver_name).get_solver_solution(user_solution)

    def get_solver_info(self, solver_name: str) -> SolverInfo:
        return self.get_solver(solver_name).get_solver_info()

    def enumerate_available(self) -> List[Tuple[str,str]]:
        solvers=requests.get(self.base_github_url_solvers).json()

        solution = [ 
            (
                self.get_solver(sol["name"][:-3]).get_solver_info()["title"],
                sol["name"][:-3]
            ) for sol in solvers if sol["name"][-3:] == ".py"
        ]
        return solution 


