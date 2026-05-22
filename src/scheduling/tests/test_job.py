'''
Tests for the Job class

@author: Vassilissa Lehoux
'''
import os
import unittest

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA


class TestJob(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCompletionTime(self):
        inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
        sol = Solution(inst)
        
        job = inst.jobs[0]
        op1, op2 = job.operations[0], job.operations[1]
        op1.end_time = 20
        op2.end_time = 45
        
        self.assertEqual(job.completion_time, 45, 'Le completion_time du Job doit être égal à la date de fin de sa dernière opération')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
