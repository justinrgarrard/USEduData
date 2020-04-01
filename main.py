"""
A driver function to build the full set of data files.
"""

import os
import logging
import create_finance_districts_csv
import create_finance_states_csv
import create_naep_states_raw_csv
import create_naep_states_csv
import create_enroll_districts_raw_csv
import create_enroll_districts_csv
import create_enroll_states_raw_csv
import create_enroll_states_csv
import create_enroll_states_summary_csv
import create_states_all_csv

# Create a shared log file
logging.basicConfig(format='%(asctime)s: %(filename)s [%(funcName)s]- %(message)s', level=logging.DEBUG)
LOGGER = logging.getLogger()

# Set shared input/output directories
INPUT_DIR = os.path.abspath('input_data')
OUTPUT_DIR = os.path.abspath('output_data')
SANITY_DIR = os.path.abspath('sanity_checks')

LOGGER.info('Starting data processing...')

# Create district and state summary files
## District
# create_finance_districts_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
## State
# create_finance_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

# Create a summary file from the NAEP data
## District

## State
# create_naep_states_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
create_naep_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

# Create a summary file from the NCES data
## District
# create_enroll_districts_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
# create_enroll_districts_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

## State
# create_enroll_states_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
# create_enroll_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)
# create_enroll_states_summary_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

# Create a summary file from all the data
## District

## State
# create_states_all_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

LOGGER.info('Data processing complete!')

