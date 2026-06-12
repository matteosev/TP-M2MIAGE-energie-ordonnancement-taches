'''
Constructive heuristics that returns preferably **feasible** solutions.

@author: Vassilissa Lehoux
'''
from typing import Dict
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.heuristics import Heuristic


class Greedy(Heuristic):
    '''
    A deterministic greedy method to return a solution.
    Strategy applied: Earliest Completion Time (ECT).
    '''

    def __init__(self, params: Dict = None):
        '''
        Constructor
        '''
        self.params = params if params is not None else {}

    def run(self, instance: Instance, params: Dict = None) -> Solution:
        '''
        Computes a solution for the given instance using a Greedy ECT strategy.
        '''
        if params is None:
            params = self.params
            
        sol = Solution(instance)
        sol.reset()
        
        available = sol.available_operations
        
        while available:
            best_op = None
            best_mach = None
            min_completion_time = float('inf')
            
            # Pour chaque opération dont les contraintes de précédence sont respectées...
            for op in available:
                prev_end = sol._get_previous_operation_end_time(op)
                
                # ... on évalue la date de fin sur chaque machine
                for mach in instance.machines:
                    
                    # Estimation rapide de la disponibilité de la machine
                    machine_ready = mach.available_time
                    if len(mach.start_times) == 0: # Si la machine est éteinte, elle nécessitera un setup
                        machine_ready = mach.set_up_time
                        
                    expected_start = max(prev_end, machine_ready)
                    expected_end = expected_start + op.processing_times[mach.machine_id]
                    
                    # Choix glouton : le couple qui termine le plus tôt gagne
                    if expected_end < min_completion_time:
                        min_completion_time = expected_end
                        best_op = op
                        best_mach = mach
                        
            # Application de l'optimum local
            sol.schedule(best_op, best_mach)
            available = sol.available_operations
            
        return sol


class NonDeterminist(Heuristic):
    '''
    Heuristic that returns different values for different runs with the same parameters
    (or different values for different seeds and otherwise same parameters)
    '''

    def __init__(self, params: Dict = None):
        '''
        Constructor
        '''
        self.params = params if params is not None else {}

    def run(self, instance: Instance, params: Dict = None) -> Solution:
        '''
        Computes a fully random valid sequence of operations.
        '''
        if params is None:
            params = self.params
            
        # Support de la reproductibilité pour le débogage
        if "seed" in params:
            random.seed(params["seed"])
            
        sol = Solution(instance)
        sol.reset()
        
        available = sol.available_operations
        
        while available:
            # 1. Sélectionne aléatoirement une opération parmi celles autorisées
            op = random.choice(available)
            
            # 2. Sélectionne aléatoirement une machine
            mach = random.choice(instance.machines)
            
            # 3. Planifie
            sol.schedule(op, mach)
            available = sol.available_operations
            
        return sol


if __name__ == "__main__":
    # Example of playing with the heuristics
    import os
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
    
    # Test Non-Déterministe
    heur_rand = NonDeterminist()
    sol_rand = heur_rand.run(inst)
    plt_rand = sol_rand.gantt("tab20")
    plt_rand.savefig("gantt_rand.png")
    
    # Test Glouton
    heur_greedy = Greedy()
    sol_greedy = heur_greedy.run(inst)
    plt_greedy = sol_greedy.gantt("tab20")
    plt_greedy.savefig("gantt_greedy.png")