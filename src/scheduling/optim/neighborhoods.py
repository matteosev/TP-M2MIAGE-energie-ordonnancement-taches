'''
Neighborhoods for solutions.
@author: Vassilissa Lehoux
'''
from typing import Dict
from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution

class Neighborhood(object):
    def __init__(self, instance: Instance, params: Dict=None):
        self._instance = instance
        self.params = params if params is not None else {}

    def best_neighbor(self, sol: Solution) -> Solution:
        raise NotImplementedError

    def first_better_neighbor(self, sol: Solution) -> Solution:
        raise NotImplementedError

    def _extract_sequence(self, sol: Solution):
        """Extrait la séquence chronologique des opérations : list de tuples (op_id, mach_id)"""
        sorted_ops = sorted(sol.all_operations, key=lambda o: o.start_time if o.start_time is not None else float('inf'))
        return [(op.operation_id, op.assigned_to) for op in sorted_ops if op.assigned]

    def _build_solution(self, sequence) -> Solution:
        """Reconstruit une solution à partir d'une séquence altérée."""
        new_sol = Solution(self._instance)
        new_sol.reset()
        for op_id, mach_id in sequence:
            op = next((o for o in new_sol.all_operations if o.operation_id == op_id), None)
            if op not in new_sol.available_operations:
                return None  # La permutation a cassé la précédence stricte des jobs
            mach = next((m for m in new_sol.inst.machines if m.machine_id == mach_id), None)
            new_sol.schedule(op, mach)
        return new_sol


class MachineReassignment(Neighborhood):
    '''
    Voisinage 1 : Modifie la machine affectée à une opération.
    '''
    def first_better_neighbor(self, sol: Solution) -> Solution:
        base_eval = sol.evaluate
        base_seq = self._extract_sequence(sol)

        for i, (op_id, mach_id) in enumerate(base_seq):
            for m in self._instance.machines:
                if m.machine_id != mach_id:
                    new_seq = list(base_seq)
                    new_seq[i] = (op_id, m.machine_id)
                    neighbor = self._build_solution(new_seq)
                    if neighbor is not None and neighbor.is_feasible and neighbor.evaluate < base_eval:
                        return neighbor
        return sol

    def best_neighbor(self, sol: Solution) -> Solution:
        best_sol = sol
        best_eval = sol.evaluate
        base_seq = self._extract_sequence(sol)

        for i, (op_id, mach_id) in enumerate(base_seq):
            for m in self._instance.machines:
                if m.machine_id != mach_id:
                    new_seq = list(base_seq)
                    new_seq[i] = (op_id, m.machine_id)
                    neighbor = self._build_solution(new_seq)
                    if neighbor is not None and neighbor.is_feasible and neighbor.evaluate < best_eval:
                        best_eval = neighbor.evaluate
                        best_sol = neighbor
        return best_sol


class SwapNeighborhood(Neighborhood):
    '''
    Voisinage 2 : Permute l'ordre de deux opérations successives.
    '''
    def first_better_neighbor(self, sol: Solution) -> Solution:
        base_eval = sol.evaluate
        base_seq = self._extract_sequence(sol)

        for i in range(len(base_seq) - 1):
            op1_id, m1_id = base_seq[i]
            op2_id, m2_id = base_seq[i+1]
            
            # Évite de permuter deux opérations du même job (cassure mathématique garantie)
            op1 = next(o for o in sol.all_operations if o.operation_id == op1_id)
            op2 = next(o for o in sol.all_operations if o.operation_id == op2_id)
            if op1.job_id != op2.job_id:
                new_seq = list(base_seq)
                new_seq[i], new_seq[i+1] = new_seq[i+1], new_seq[i]
                neighbor = self._build_solution(new_seq)
                if neighbor is not None and neighbor.is_feasible and neighbor.evaluate < base_eval:
                    return neighbor
        return sol

    def best_neighbor(self, sol: Solution) -> Solution:
        best_sol = sol
        best_eval = sol.evaluate
        base_seq = self._extract_sequence(sol)

        for i in range(len(base_seq) - 1):
            op1_id, m1_id = base_seq[i]
            op2_id, m2_id = base_seq[i+1]
            
            op1 = next(o for o in sol.all_operations if o.operation_id == op1_id)
            op2 = next(o for o in sol.all_operations if o.operation_id == op2_id)
            if op1.job_id != op2.job_id:
                new_seq = list(base_seq)
                new_seq[i], new_seq[i+1] = new_seq[i+1], new_seq[i]
                neighbor = self._build_solution(new_seq)
                if neighbor is not None and neighbor.is_feasible and neighbor.evaluate < best_eval:
                    best_eval = neighbor.evaluate
                    best_sol = neighbor
        return best_sol