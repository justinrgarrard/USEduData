"""
A driver function to build the full set of data files.
"""

import logging
import create_finance_districts_csv
import create_finance_states_csv
import create_naep_states_csv
import create_enroll_states_csv
import create_states_all_csv
import data_sanity_check

# Create a shared log file
logging.basicConfig(format='%(asctime)s: %(filename)s [%(funcName)s]- %(message)s', level=logging.DEBUG)
LOGGER = logging.getLogger()

LOGGER.info('Starting data processing...')

# Create district summary file
create_finance_districts_csv.main(LOGGER)

# Create state summary file from district summary
create_finance_states_csv.main(LOGGER)

# Create a summary file from the NAEP data
create_naep_states_csv.main(LOGGER)

# Create a summary file from the NCES data
create_enroll_states_csv.main(LOGGER)

# Create a denormalized file from all the data
create_states_all_csv.main(LOGGER)

# Create a sanity check file from the aggregated data
data_sanity_check.main(LOGGER)

LOGGER.info('Data processing complete!')

