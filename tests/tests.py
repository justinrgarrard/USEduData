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
    def test_csv_to_standard(self):
        # Load in data
        output_filename = 'finance_districts.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        ## Uses a hardcoded value from the source spreadsheet for input
        input_val = 281989

        output_row = output_data[output_data['YRDATA'] == 2016]
        output_row = output_row[output_row['STATE'] == 'IDAHO']
        output_row = output_row[output_row['NAME'] == 'MERIDIAN SCHOOL DISTRICT 2']
        output_val = output_row['TOTALREV'].iloc[0]

        assert (input_val == output_val)


class FinanceStatePipelineTests(unittest.TestCase):
    def test_district_to_state(self):
        # Load in data
        input_filename = 'finance_districts.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'finance_states.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['YRDATA'] == 2016]
        input_row = input_row[input_row['STATE'] == 'IDAHO']
        input_val = input_row['TOTALREV'].sum()

        output_row = output_data[output_data['PRIMARY_KEY'] == '2016_IDAHO']
        output_val = output_row['TOTAL_REVENUE'].iloc[0]

        assert (input_val == output_val)

    def test_standard_to_all(self):
        # Load in data
        input_filename = 'finance_states.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'states_all.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['PRIMARY_KEY'] == '2016_IDAHO']
        input_val = input_row['TOTAL_REVENUE'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2016_IDAHO']
        output_val = output_row['TOTAL_REVENUE'].iloc[0]

        assert (input_val == output_val)


class EnrollDistrictPipelineTests(unittest.TestCase):
    def test_csv_to_raw(self):
        # Load in data
        output_filename = 'enroll_districts_raw.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        ## Uses a hardcoded value from the source spreadsheet for input
        input_val = 15585

        output_row = output_data[output_data['State Name'] == 'IDAHO']
        output_row = output_row[output_row['Agency Name'] == 'NAMPA SCHOOL DISTRICT']
        output_val = output_row['2017_A_A_A'].iloc[0]

        assert (input_val == output_val)

    def test_raw_to_standard(self):
        # Load in data
        input_filename = 'enroll_districts_raw.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'enroll_districts.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['State Name'] == 'IDAHO']
        input_row = input_row[input_row['Agency Name'] == 'NAMPA SCHOOL DISTRICT']
        input_val = input_row['2017_A_A_A'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2017_NAMPA SCHOOL DISTRICT']
        output_val = output_row['A_A_A'].iloc[0]

        assert (input_val == output_val)


class EnrollStatePipelineTests(unittest.TestCase):
    def test_csv_to_raw(self):
        # Load in data
        output_filename = 'enroll_states_raw.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        ## Uses a hardcoded value from the source spreadsheet for input
        input_val = 301186

        output_row = output_data[output_data['State Name'] == 'IDAHO']
        output_val = output_row['2017_A_A_A'].iloc[0]

        assert (input_val == output_val)

    def test_raw_to_standard(self):
        # Load in data
        input_filename = 'enroll_states_raw.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'enroll_states.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['State Name'] == 'IDAHO']
        input_val = input_row['2017_A_A_A'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2017_IDAHO']
        output_val = output_row['A_A_A'].iloc[0]

        assert (input_val == output_val)

    def test_standard_to_summary(self):
        # Load in data
        input_filename = 'enroll_states.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'enroll_states_summary.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['PRIMARY_KEY'] == '2017_IDAHO']
        input_val = input_row['A_A_A'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2017_IDAHO']
        output_val = output_row['GRADES_ALL_G'].iloc[0]

        assert (input_val == output_val)

    def test_standard_to_all(self):
        # Load in data
        input_filename = 'enroll_states.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'states_all.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['PRIMARY_KEY'] == '2017_IDAHO']
        input_val = input_row['A_A_A'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2017_IDAHO']
        output_val = output_row['GRADES_ALL_G'].iloc[0]

        assert (input_val == output_val)


class AchievementStatePipelineTests(unittest.TestCase):
    def test_csv_to_raw(self):
        # Load in data
        output_filename = 'naep_states_raw.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        ## Uses a hardcoded value from the source spreadsheet for input
        input_val = 223

        output_row = output_data[output_data['YEAR'] == 2019]
        output_row = output_row[output_row['STATE'] == 'IDAHO']
        output_row = output_row[output_row['DEMO'] == 'G04_A_A']
        output_row = output_row[output_row['TEST_SUBJECT'] == 'Reading']
        output_val = output_row['AVG_SCORE'].iloc[0]

        assert (input_val == output_val)

    def test_raw_to_standard(self):
        # Load in data
        input_filename = 'naep_states_raw.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'naep_states.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['YEAR'] == 2019]
        input_row = input_row[input_row['STATE'] == 'IDAHO']
        input_row = input_row[input_row['DEMO'] == 'G04_A_A']
        input_row = input_row[input_row['TEST_SUBJECT'] == 'Reading']
        input_val = input_row['AVG_SCORE'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2019_IDAHO']
        output_val = output_row['G04_A_A_READING'].iloc[0]

        assert(input_val == output_val)

    def test_standard_to_summary(self):
        # Load in data
        input_filename = 'naep_states.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'naep_states_summary.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['PRIMARY_KEY'] == '2019_IDAHO']
        input_val = input_row['G04_A_A_READING'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2019_IDAHO']
        output_val = output_row['AVG_READING_4_SCORE'].iloc[0]

        assert (input_val == output_val)

    def test_standard_to_all(self):
        # Load in data
        input_filename = 'naep_states.csv'
        input_data = pd.read_csv(os.path.join(OUTPUT_DIR, input_filename))
        output_filename = 'states_all_extended.csv'
        output_data = pd.read_csv(os.path.join(OUTPUT_DIR, output_filename))

        # Test one entry to ensure that the transformed value matches
        input_row = input_data[input_data['PRIMARY_KEY'] == '2019_IDAHO']
        input_val = input_row['G04_A_A_READING'].iloc[0]

        output_row = output_data[output_data['PRIMARY_KEY'] == '2019_IDAHO']
        output_val = output_row['G04_A_A_READING'].iloc[0]

        assert (input_val == output_val)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
