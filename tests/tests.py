"""
A testing script that evaluates each pipeline.

Should only be run AFTER the main script has executed and
output files have been generated.
"""

import os
import time
import shutil
import pandas as pd
import unittest
import zipfile

# Set shared input/output directories
INPUT_DIR = os.path.abspath('../input_data')
OUTPUT_DIR = os.path.abspath('../output_data')
SANITY_DIR = os.path.abspath('../sanity_checks')


class FinanceDistrictPipelineTests(unittest.TestCase):
    pass


class FinanceStatePipelineTests(unittest.TestCase):
    pass


class EnrollDistrictPipelineTests(unittest.TestCase):
    pass


class AchievementStatePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Unpack the data
        zip_name = 'NAEP_ASSESS_STATES.zip'
        input_data_path = os.path.join(INPUT_DIR, zip_name)
        input_data = zipfile.ZipFile(input_data_path, 'r')
        file_list = input_data.namelist()
        file_list.remove(zip_name.strip('.zip') + '/')
        input_data.extractall(os.getcwd())
        input_data.close()

    @classmethod
    def tearDownClass(cls):
        # Remove extracted data directory
        zip_name = 'NAEP_ASSESS_STATES.zip'
        shutil.rmtree(zip_name.strip('.zip') + '/')

    def test_state_csv_to_raw(self):
        pass

    def test_state_raw_to_standard(self):
        # Load in data
        input_filename = 'naep_states_raw.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'naep_states.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test an individual cell
        input_row = input_data[input_data['YEAR'] == 2019]
        input_row = input_row[input_data['STATE'] == 'IDAHO']
        input_row = input_row[input_data['DEMO'] == 'G04_A_A']
        input_row = input_row[input_data['TEST_SUBJECT'] == 'Reading']
        input_val = input_row['AVG_SCORE'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2019_IDAHO']
        output_val = output_row['G04_A_A_READING'].iloc[0]

        assert(input_val == output_val)

    def test_state_standard_to_summary(self):
        pass


class EnrollStatePipelineTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main(warnings='ignore')
