'''
Operation of a job.
Its duration and energy consumption depends on the machine on which it is executed.
When operation is scheduled, its schedule information is updated.

@author: Vassilissa Lehoux
'''
from typing import List


class OperationScheduleInfo(object):
    '''
    Informations known when the operation is scheduled
    '''

    def __init__(self, machine_id: int, schedule_time: int, duration: int, energy_consumption: int):
        raise "Not implemented error"


class Operation(object):
    '''
    Operation of the jobs
    '''

    def __init__(self, job_id, operation_id):
        '''
        Constructor
        '''
        self._job_id = job_id
        self._operation_id = operation_id
        
        # Dictionnaires pour stocker les coûts selon la machine : {machine_id: valeur}
        self.processing_times = {} 
        self.energy_consumptions = {}
        
        # Variables de décision (état de la solution)
        self._assigned = False
        self._assigned_to = None
        self._start_time = None
        self._end_time = None

    def __str__(self):
        '''
        Returns a string representing the operation.
        '''
        base_str = f"O{self.operation_id}_J{self.job_id}"
        if self._schedule_info:
            return base_str + f"_M{self.assigned_to}_ci{self.processing_time}_e{self.energy}"
        else:
            return base_str

    def __repr__(self):
        return f"Op(id={self.operation_id}, job={self.job_id})"

    def reset(self):
        '''
        Removes scheduling informations
        '''
        self._assigned = False
        self._assigned_to = None
        self._start_time = None
        self._end_time = None

    def add_predecessor(self, operation):
        '''
        Adds a predecessor to the operation
        '''
        raise "Not implemented error"

    def add_successor(self, operation):
        '''
        Adds a successor operation
        '''
        raise "Not implemented error"

    @property
    def operation_id(self) -> int:
        return self._operation_id

    @property
    def job_id(self) -> int:
        return self._job_id

    @property
    def predecessors(self) -> List:
        """
        Returns a list of the predecessor operations
        """
        raise "Not implemented error"

    @property
    def successors(self) -> List:
        '''
        Returns a list of the successor operations
        '''
        raise "Not implemented error"

    @property
    def assigned(self) -> bool:
        '''
        Returns True if the operation is assigned
        and False otherwise
        '''
        return self._assigned or False

    @property
    def assigned_to(self) -> int:
        '''
        Returns the machine ID it is assigned to if any
        and -1 otherwise
        '''
        return self._assigned_to if self._assigned_to is not None else -1

    @property
    def processing_time(self) -> int:
        '''
        Returns the processing time if is assigned,
        -1 otherwise
        '''
        if self.assigned_to is not None:
            return self.processing_times.get(self.assigned_to)
        return 0

    @property
    def start_time(self) -> int:
        '''
        Returns the start time if is assigned,
        -1 otherwise
        '''
        return self._start_time if self._start_time is not None else -1

    @property
    def end_time(self) -> int:
        '''
        Returns the end time if is assigned,
        -1 otherwise
        '''
        return self._end_time if self._end_time is not None else -1

    @property
    def energy(self) -> int:
        '''
        Returns the energy consumption if is assigned,
        -1 otherwise
        '''
        if self.assigned_to is not None:
            return self.energy_consumptions.get(self.assigned_to)
        return 0

    def is_ready(self, at_time) -> bool:
        '''
        Returns True if all the predecessors are assigned
        and processed before at_time.
        False otherwise
        '''
        raise "Not implemented error"

    def schedule(self, machine_id: int, at_time: int, check_success=True) -> bool:
        '''
        Schedules an operation. Updates the schedule information of the operation
        @param check_success: if True, check if all the preceeding operations have
          been scheduled and if the schedule time is compatible
        '''
        raise "Not implemented error"

    @property
    def min_start_time(self) -> int:
        '''
        Minimum start time given the precedence constraints
        '''
        raise "Not implemented error"

    def schedule_at_min_time(self, machine_id: int, min_time: int) -> bool:
        '''
        Try and schedule the operation af or after min_time.
        Return False if not possible
        '''
        raise "Not implemented error"
