'''
Information for the instance of the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List
import os
import csv

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation
from src.scheduling.instance.machine import Machine


class Instance(object):
    '''
    classdocs
    '''

    def __init__(self, instance_name):
        '''
        Constructor
        '''
        self._name = instance_name
        self._machines: List[Machine] = []
        self._jobs: List[Job] = []
        self._operations: List[Operation] = []

    @classmethod
    def from_file(cls, folderpath):
        name = os.path.basename(os.path.normpath(folderpath))
        inst = cls(name)

        mach_file = os.path.join(folderpath, f"{name}_mach.csv")
        op_file = os.path.join(folderpath, f"{name}_op.csv")

        # Parsing des machines
        with open(mach_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = Machine(
                    machine_id=row['machine_id'],
                    set_up_time=row['set_up_time'],
                    set_up_energy=row['set_up_energy'],
                    tear_down_time=row['tear_down_time'],
                    tear_down_energy=row['tear_down_energy'],
                    min_consumption=row['min_consumption'],
                    end_time=row['end_time']
                )
                inst.machines.append(m)

        # Parsing des opérations
        job_dict = {}
        op_dict = {}

        with open(op_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                j_id = int(row['job'])
                o_id = int(row['operation'])
                m_id = int(row['machine'])
                p_time = int(row['processing_time'])
                e_cons = int(row['energy_consumption'])

                # Création du Job s'il n'existe pas encore
                if j_id not in job_dict:
                    job = Job(j_id)
                    job_dict[j_id] = job
                    inst.jobs.append(job)
                
                # Création de l'opération si elle n'existe pas encore
                op_key = (j_id, o_id)
                if op_key not in op_dict:
                    op = Operation(j_id, o_id)
                    op_dict[op_key] = op
                    inst.operations.append(op)
                    job_dict[j_id].add_operation(op)

                # Ajout de la configuration pour cette machine spécifique
                op = op_dict[op_key]
                op.processing_times[m_id] = p_time
                op.energy_consumptions[m_id] = e_cons

        # Tri pour correspondre aux index
        inst.machines.sort(key=lambda x: x.machine_id)
        inst.jobs.sort(key=lambda x: x.job_id)
        inst.operations.sort(key=lambda x: x.operation_id)
        
        return inst

    @property
    def name(self):
        return self._name

    @property
    def machines(self) -> List[Machine]:
        return self._machines

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    @property
    def operations(self) -> List[Operation]:
        return self._operations

    @property
    def nb_jobs(self):
        return self._nb_jobs

    @property
    def nb_machines(self):
        return len(self._machines)

    @property
    def nb_operations(self):
        return self._nb_operations

    def __str__(self):
        return f"{self.name}_M{self.nb_machines}_J{self.nb_jobs}_O{self.nb_operations}"

    def get_machine(self, machine_id) -> Machine:
        return self.machines[machine_id]

    def get_job(self, job_id) -> Job:
        return self.jobs[job_id]

    def get_operation(self, operation_id) -> Operation:
        return self.operations[operation_id]
