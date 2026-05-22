'''
Job. It is composed of several operations.

@author: Vassilissa Lehoux
'''
from typing import List

from src.scheduling.instance.operation import Operation


class Job(object):
    '''
    Job class.
    Contains information on the next operation to schedule for that job
    '''

    def __init__(self, job_id: int):
        '''
        Constructor
        '''
        self._job_id = job_id
        self._operations: List[Operation] = []
        
    @property
    def job_id(self) -> int:
        '''
        Returns the id of the job.
        '''
        return self._job_id

    def reset(self):
        '''
        Resets the planned operations
        '''
        raise "Not implemented error"

    @property
    def operations(self) -> List[Operation]:
        '''
        Returns a list of operations for the job
        '''
        return self._operations

    @property
    def next_operation(self) -> Operation:
        '''
        Returns the next operation to be scheduled
        '''
        raise "Not implemented error"

    def schedule_operation(self):
        '''
        Updates the next_operation to schedule
        '''
        raise "Not implemented error"

    @property
    def planned(self):
        '''
        Returns true if all operations are planned
        '''
        raise "Not implemented error"

    @property
    def operation_nb(self) -> int:
        '''
        Returns the nb of operations of the job
        '''
        raise "Not implemented error"

    def add_operation(self, operation: Operation):
        '''
        Adds an operation to the job at the end of the operation list,
        adds the precedence constraints between job operations.
        '''
        self.operations.append(operation)

    @property
    def completion_time(self) -> int:
        '''
        Returns the job's completion time
        '''
        if not self.operations:
            return 0
        
        # On cherche l'opération qui se termine le plus tard parmi celles assignées
        completed_ops = [op for op in self.operations if op.assigned and op.end_time is not None]
        if not completed_ops:
            return 0
            
        return max(op.end_time for op in completed_ops)
    
    def __repr__(self):
        return f"Job(id={self.job_id}, ops={len(self.operations)})"
