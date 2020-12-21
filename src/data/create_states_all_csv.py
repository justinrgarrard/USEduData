"""
A script for creating adding additional data to the states.csv file (such as
the NAEP data).
"""

import os
import re
import pandas as pd
import us  # US metadata, like state names
from src.data import data_sanity_check

FINANCE_FILENAME = 'finance_states.csv'
ENROLL_FILENAME = 'enroll_states_summary.csv'
ENROLL_EXTENDED_FILENAME = 'enroll_states.csv'
ACHIEVE_FILENAME = 'naep_states_summary.csv'
ACHIEVE_EXTENDED_FILENAME = 'naep_states.csv'

OUTPUT_FILENAME = 'states_all.csv'
OUTPUT_EXTENDED_FILENAME = 'states_all_extended.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Creating aggregate file...')

    # Combine data
    finance_data = pd.read_csv(os.path.join(input_dir, FINANCE_FILENAME))
    enroll_data = pd.read_csv(os.path.join(input_dir, ENROLL_FILENAME))
    achieve_data = pd.read_csv(os.path.join(input_dir, ACHIEVE_FILENAME))

    all_data = finance_data.merge(enroll_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data = all_data.merge(achieve_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data.sort_values(['YEAR', 'STATE'])

    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    all_data.to_csv(output_path, index=False)

    # Combine extended data
    finance_data_extend = pd.read_csv(os.path.join(input_dir, FINANCE_FILENAME))
    enroll_data_extend = pd.read_csv(os.path.join(input_dir, ENROLL_EXTENDED_FILENAME))
    achieve_data_extend = pd.read_csv(os.path.join(input_dir, ACHIEVE_EXTENDED_FILENAME))

    all_data_extend = finance_data_extend.merge(enroll_data_extend, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data_extend = all_data_extend.merge(achieve_data_extend, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data_extend.sort_values(['YEAR', 'STATE'])

    output_path = os.path.join(output_dir, OUTPUT_EXTENDED_FILENAME)
    all_data_extend.to_csv(output_path, index=False)

    # Sanity check
    data_sanity_check.main(logger, output_dir, sanity_dir, OUTPUT_FILENAME, count_year_nulls=True)


if __name__ == '__main__':
    main()
