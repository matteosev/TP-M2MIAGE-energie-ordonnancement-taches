'''
Machine on which operation are executed.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.operation import Operation


class Machine(object):
    '''
    Machine class.
    When operations are scheduled on the machine, contains the relative information. 
    '''

    def __init__(self, machine_id: int, set_up_time: int, set_up_energy: int, tear_down_time: int,
                 tear_down_energy:int, min_consumption: int, end_time: int):
        '''
        Constructor
        Machine is stopped at the beginning of the planning and need to
        be started before executing any operation.
        @param end_time: End of the schedule on this machine: the machine must be
          shut down before that time.
        '''
        self._machine_id = int(machine_id)
        self._set_up_time = int(set_up_time)
        self.set_up_energy = int(set_up_energy)
        self._tear_down_time = int(tear_down_time)
        self.tear_down_energy = int(tear_down_energy)
        self.min_consumption = float(min_consumption)
        self.end_time = int(end_time)

        # État de l'ordonnancement
        self._scheduled_operations: List[Operation] = []
        self._start_times: List[int] = []
        self._stop_times: List[int] = []

    def reset(self):
        self.scheduled_operations.clear()
        self.start_times.clear()
        self.stop_times.clear()

    @property
    def set_up_time(self) -> int:
        return self._set_up_time

    @property
    def tear_down_time(self) -> int:
        return self._tear_down_time

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @property
    def scheduled_operations(self) -> List:
        '''
        Returns the list of the scheduled operations on the machine.
        '''
        return self._scheduled_operations

    @property
    def available_time(self) -> int:
        """
        Returns the next time at which the machine is available
        after processing its last operation of after its last set up.
        """
        if not self.scheduled_operations:
            return 0
        return max(op.end_time for op in self.scheduled_operations)

    def add_operation(self, operation: Operation, start_time: int) -> int:
        '''
        Adds an operation on the machine, at the end of the schedule,
        as soon as possible after time start_time.
        Returns the actual start time.
        '''
        raise "Not implemented error"
  
    def stop(self, at_time):
        """
        Stops the machine at time at_time.
        """
        assert(self.available_time >= at_time)
        raise "Not implemented error"

    @property
    def working_time(self) -> int:
        '''
        Total time during which the machine is running
        '''
        return sum(stop - start for start, stop in zip(self.start_times, self.stop_times))

    @property
    def start_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is started
        in increasing order
        """
        return self._start_times

    @property
    def stop_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is stopped
        in increasing order
        """
        return self._stop_times

    @property
    def total_energy_consumption(self) -> float:
        """
        Total energy consumption of the machine during planning exectution.
        """
        nb_cycles = len(self.start_times)
        if nb_cycles == 0:
            return 0.0

        # Énergie d'allumage et d'extinction
        energy_transitions = nb_cycles * (self.set_up_energy + self.tear_down_energy)
        
        # Énergie consommée par les opérations actives
        energy_ops = sum(op.energy for op in self.scheduled_operations)
        
        # Énergie consommée pendant que la machine est allumée mais inactive (en veille)
        total_ops_time = sum(op.processing_time for op in self.scheduled_operations)
        total_transitions_time = nb_cycles * (self.set_up_time + self.tear_down_time)
        idle_time = self.working_time - total_transitions_time - total_ops_time
        energy_idle = idle_time * self.min_consumption
        
        return energy_transitions + energy_ops + energy_idle

    def __str__(self):
        return f"M{self.machine_id}"

    def __repr__(self):
        return str(self)
