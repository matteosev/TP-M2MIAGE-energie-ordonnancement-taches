'''
Tests for the Machine class

@author: Vassilissa Lehoux
'''
import os
import unittest

from src.scheduling.instance.instance import Instance
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA


class TestMachine(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testWorkingTime(self):
        inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
        machine = inst.machines[0]
        
        # Simulation d'un cycle d'allumage/extinction
        machine.start_times.append(10)
        machine.start_times.append(50)
        machine.stop_times.append(30)
        machine.stop_times.append(80)

        # (30 - 10) + (80 - 50) = 20 + 30 = 50
        self.assertEqual(machine.working_time, 50, 'Le working_time doit être la somme des durées de fonctionnement actives')

    def testTotalEnergyConsumption(self):
        pass



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()