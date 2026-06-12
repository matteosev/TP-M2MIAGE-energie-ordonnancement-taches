'''
Heuristics that compute an initial solution and then improve it.
@author: Vassilissa Lehoux
'''
import os
import time
from typing import Dict, List

from src.scheduling.optim.heuristics import Heuristic
from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.constructive import NonDeterminist, Greedy
from src.scheduling.optim.neighborhoods import MachineReassignment, SwapNeighborhood
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA

class FirstNeighborLocalSearch(Heuristic):
    '''
    Utilise UN SEUL voisinage.
    Dès qu'un voisin strictement meilleur est trouvé, on l'adopte et on recommence.
    '''
    def __init__(self, params: Dict=None):
        self.params = params if params is not None else {}

    def run(self, instance: Instance, InitClass, NeighborClass, params: Dict=None) -> Solution:
        p = params if params is not None else self.params
        init_heur = InitClass(p)
        current_sol = init_heur.run(instance, p)
        neighborhood = NeighborClass(instance, p)

        while True:
            # On cherche la première amélioration possible
            neighbor = neighborhood.first_better_neighbor(current_sol)
            if neighbor.evaluate < current_sol.evaluate:
                current_sol = neighbor
            else:
                # Optima local atteint, on s'arrête
                break
        return current_sol


class BestNeighborLocalSearch(Heuristic):
    '''
    Utilise DEUX voisinages combinés.
    Explore l'intégralité des deux voisinages et retient la meilleure amélioration absolue.
    Ajout d'un critère d'arrêt : max_iter pour éviter les boucles infinies sur les plateaux.
    '''
    def __init__(self, params: Dict=None):
        self.params = params if params is not None else {}

    def run(self, instance: Instance, InitClass, NeighborClasses: List, params: Dict=None) -> Solution:
        p = params if params is not None else self.params
        init_heur = InitClass(p)
        current_sol = init_heur.run(instance, p)
        neighborhoods = [NC(instance, p) for NC in NeighborClasses]
        
        max_iter = p.get('max_iter', 50)
        iterations = 0

        while iterations < max_iter:
            best_overall_neighbor = current_sol
            
            # On sonde les deux voisinages pour trouver la "pépite"
            for nh in neighborhoods:
                candidate = nh.best_neighbor(current_sol)
                if candidate.evaluate < best_overall_neighbor.evaluate:
                    best_overall_neighbor = candidate

            if best_overall_neighbor.evaluate < current_sol.evaluate:
                current_sol = best_overall_neighbor
                iterations += 1
            else:
                # Optima local globalement atteint
                break
                
        return current_sol


if __name__ == "__main__":
    # === SCRIPT DE COMPARAISON GLOBAL ===
    instances_to_test = ["jsp1", "jsp2", "jsp3"] # Test sur quelques instances
    nb_runs_nondeterministe = 5 # Nombre d'essais pour mitiger la part d'aléatoire
    
    print(f"{'Instance':<10} | {'Algo':<25} | {'Score (Energie/Temps)':<25} | {'Temps calcul (s)':<15}")
    print("-" * 80)

    for inst_name in instances_to_test:
        inst_path = os.path.join(TEST_FOLDER_DATA, inst_name)
        if not os.path.exists(inst_path):
            continue
            
        inst = Instance.from_file(inst_path)

        # 1. Glouton (Base de référence déterministe)
        t_start = time.time()
        greedy_heur = Greedy()
        sol_greedy = greedy_heur.run(inst)
        t_greedy = time.time() - t_start
        print(f"{inst_name:<10} | {'Greedy (ECT)':<25} | {sol_greedy.evaluate:<25.2f} | {t_greedy:<15.4f}")

        # 2. Local Search : First Improvement (1 voisinage : Changement Machine)
        best_fi_score = float('inf')
        t_start = time.time()
        for _ in range(nb_runs_nondeterministe):
            ls_fi = FirstNeighborLocalSearch()
            # On utilise le Neighborhood 1 pour ce test
            sol_fi = ls_fi.run(inst, NonDeterminist, MachineReassignment)
            if sol_fi.evaluate < best_fi_score:
                best_fi_score = sol_fi.evaluate
        t_fi = time.time() - t_start
        print(f"{inst_name:<10} | {'LS First (N1)':<25} | {best_fi_score:<25.2f} | {t_fi:<15.4f}")

        # 3. Local Search : Best Improvement (2 voisinages combinés)
        best_bi_score = float('inf')
        t_start = time.time()
        for _ in range(nb_runs_nondeterministe):
            ls_bi = BestNeighborLocalSearch()
            sol_bi = ls_bi.run(inst, NonDeterminist, [MachineReassignment, SwapNeighborhood])
            if sol_bi.evaluate < best_bi_score:
                best_bi_score = sol_bi.evaluate
        t_bi = time.time() - t_start
        print(f"{inst_name:<10} | {'LS Best (N1 + N2)':<25} | {best_bi_score:<25.2f} | {t_bi:<15.4f}")
        print("-" * 80)