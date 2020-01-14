"""
A driver function to build the full set of data files.
"""

import os
import logging
import create_finance_districts_csv
import create_finance_states_csv
import create_naep_states_csv
import create_enroll_states_raw_csv
import create_enroll_states_csv
import create_enroll_states_legacy_csv
import create_states_all_csv
import data_sanity_check
import enroll_sanity_check

# Create a shared log file
logging.basicConfig(format='%(asctime)s: %(filename)s [%(funcName)s]- %(message)s', level=logging.DEBUG)
LOGGER = logging.getLogger()

# Set shared input/output directories
INPUT_DIR = os.path.abspath('input_data')
OUTPUT_DIR = os.path.abspath('output_data')

LOGGER.info('Starting data processing...')

# Create district and state summary files
# create_finance_districts_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR)
# create_finance_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR)

# Create a summary file from the NAEP data
# create_naep_states_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR)

# Create a summary file from the NCES data
# create_enroll_states_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR)
create_enroll_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR)
# enroll_sanity_check.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR)

# Create a denormalized file from all the data
# create_states_all_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR)
# data_sanity_check.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR)

LOGGER.info('Data processing complete!')

