'''
Object containing the solution to the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List
from matplotlib import pyplot as plt
from src.scheduling.instance.instance import Instance
from src.scheduling.instance.operation import Operation

from matplotlib import colormaps
from src.scheduling.instance.machine import Machine


class Solution(object):
    '''
    Solution class
    '''

    def __init__(self, instance: Instance):
        '''
        Constructor
        '''
        self._instance = instance


    @property
    def inst(self):
        '''
        Returns the associated instance
        '''
        return self._instance


    def reset(self):
        '''
        Resets the solution: everything needs to be replanned
        '''
        for machine in self.inst.machines:
            machine.reset()
        for operation in self.all_operations:
            operation.reset()

    @property
    def is_feasible(self) -> bool:
        '''
        Returns True if the solution respects the constraints.
        To call this function, all the operations must be planned.
        '''
        # 1. Toutes les opérations doivent être planifiées
        for op in self.all_operations:
            if not op.assigned:
                return False

        # 2. Vérification des durées limites par machine (EndTime)
        for machine in self.inst.machines:
            if machine.scheduled_operations:
                last_end = max(op.end_time for op in machine.scheduled_operations)
                if last_end > machine.end_time:
                    return False

        # 3. Ordre séquentiel et non-chevauchement
        for job in self.inst.jobs:
            prev_end = 0
            for op in job.operations:
                if op.start_time < prev_end:
                    return False
                prev_end = op.end_time

        # 4. Pas de chevauchement sur les machines
        for machine in self.inst.machines:
            ops = sorted(machine.scheduled_operations, key=lambda x: x.start_time)
            prev_end = 0
            for op in ops:
                if op.start_time < prev_end:
                    return False
                prev_end = op.end_time

        return True

    @property
    def evaluate(self) -> float:
        '''
        Computes the value of the solution
        '''
        if self.is_feasible:
            return self.objective
        else:
            # Pénalité : on compte le nombre d'opérations non assignées
            unassigned_count = sum(1 for op in self.all_operations if not op.assigned)
            penalty_weight = 100000 
            return self.objective + (penalty_weight * max(1, unassigned_count))

    @property
    def objective(self) -> float:
        '''
        Returns the value of the objective function
        '''
        return float(self.cmax) + self.total_energy_consumption

    @property
    def cmax(self) -> int:
        '''
        Returns the maximum completion time of a job
        '''
        if not self.inst.jobs:
            return 0
        return max(job.completion_time for job in self.inst.jobs)

    @property
    def sum_ci(self) -> int:
        '''
        Returns the sum of completion times of all the jobs
        '''
        return sum(job.completion_time for job in self.inst.jobs)

    @property
    def total_energy_consumption(self) -> float:
        '''
        Returns the total energy consumption for processing
        all the jobs (including energy for machine switched on but doing nothing).
        '''
        return sum(machine.total_energy_consumption for machine in self.inst.machines)

    def __str__(self) -> str:
        '''
        String representation of the solution
        '''
        return ""

    def to_csv(self):
        '''
        Save the solution to a csv files with the following formats:
        Operation file:
          One line per operation
          operation id - machine to which it is assigned - start time
          header: "operation_id,machine_id,start_time"
        Machine file:
          One line per pair of (start time, stop time) for the machine
          header: "machine_id, start_time, stop_time"
        '''
        raise "Not implemented error"

    def from_csv(self, inst_folder, operation_file, machine_file):
        '''
        Reads a solution from the instance folder
        '''
        raise "Not implemented error"

    @property
    def available_operations(self)-> List[Operation]:
        '''
        Returns the available operations for scheduling:
        all constraints have been met for those operations to start
        '''
        available = []
        for job in self.inst.jobs:
            for i, op in enumerate(job.operations):
                if not op.assigned:
                    if i == 0 or job.operations[i-1].assigned:
                        available.append(op)
                    # On s'arrête à la première non assignée pour ce job (ordre séquentiel strict)
                    break 
        return available

    @property
    def all_operations(self) -> List[Operation]:
        '''
        Returns all the operations in the instance
        '''
        return self.inst.operations

    def _get_previous_operation_end_time(self, operation: Operation) -> int:
        """Helper pour trouver l'heure de fin de l'opération précédente du même job"""
        job = next(j for j in self.inst.jobs if j.job_id == operation.job_id)
        idx = job.operations.index(operation)
        if idx > 0 and job.operations[idx-1].assigned:
            return job.operations[idx-1].end_time
        return 0
    
    def schedule(self, operation: Operation, machine: Machine):
        '''
        Schedules the operation at the end of the planning of the machine.
        Starts the machine if stopped.
        @param operation: an operation that is available for scheduling
        '''
        assert(operation in self.available_operations)

        # Quelle est la contrainte de temps côté Job (l'opération précédente doit être finie)
        earliest_job_start = self._get_previous_operation_end_time(operation)

        is_machine_stopped = len(machine.start_times) == 0
        
        if is_machine_stopped:
            # Si on l'allume, elle a besoin de son temps de setup AVANT de démarrer
            op_start_time = max(earliest_job_start, machine.set_up_time)
            
            # La machine s'allume juste à temps pour être prête
            machine.start_times.append(op_start_time - machine.set_up_time)
            machine.stop_times.append(machine.end_time)
        else:
            # La machine est déjà allumée, elle peut prendre l'op dès qu'elle est dispo
            op_start_time = max(earliest_job_start, machine.available_time)

        operation._assigned = True
        operation._assigned_to = machine.machine_id
        operation._start_time = op_start_time
        operation._end_time = op_start_time + operation.processing_time

        machine.scheduled_operations.append(operation)

    def gantt(self, colormapname):
        """
        Generate a plot of the planning.
        Standard colormaps can be found at https://matplotlib.org/stable/users/explain/colors/colormaps.html
        """
        fig, ax = plt.subplots()
        colormap = colormaps[colormapname]
        for machine in self.inst.machines:
            machine_operations = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
            for operation in machine_operations:
                operation_start = operation.start_time
                operation_end = operation.end_time
                operation_duration = operation_end - operation_start
                operation_label = f"O{operation.operation_id}_J{operation.job_id}"
    
                # Set color based on job ID
                color_index = operation.job_id + 2
                if color_index >= colormap.N:
                    color_index = color_index % colormap.N
                color = colormap(color_index)
    
                ax.broken_barh(
                    [(operation_start, operation_duration)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=color,
                    edgecolor='black'
                )

                middle_of_operation = operation_start + operation_duration / 2
                ax.text(
                    middle_of_operation,
                    machine.machine_id,
                    operation_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
            set_up_time = machine.set_up_time
            tear_down_time = machine.tear_down_time
            for (start, stop) in zip(machine.start_times, machine.stop_times):
                start_label = "set up"
                stop_label = "tear down"
                ax.broken_barh(
                    [(start, set_up_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(0),
                    edgecolor='black'
                )
                ax.broken_barh(
                    [(stop, tear_down_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(1),
                    edgecolor='black'
                )
                ax.text(
                    start + set_up_time / 2.0,
                    machine.machine_id,
                    start_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
                ax.text(
                    stop + tear_down_time / 2.0,
                    machine.machine_id,
                    stop_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )          

        fig = ax.figure
        fig.set_size_inches(12, 6)
    
        ax.set_yticks(range(self._instance.nb_machines))
        ax.set_yticklabels([f'M{machine_id+1}' for machine_id in range(self.inst.nb_machines)])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Gantt Chart')
        ax.grid(True)
    
        return plt
