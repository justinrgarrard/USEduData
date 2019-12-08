"""
A script for creating adding additional data to the states.csv file (such as
the NAEP data).
"""

import os
import re
import numpy as np
import pandas as pd
import us  # US metadata, like state names

FINANCE_FILENAME = 'finance_states.csv'
ENROLL_FILENAME = 'enroll_states.csv'
ENROLL_EXTENDED_FILENAME = 'enroll_states_extended.csv'
ACHIEVE_FILENAME = 'naep_states.csv'

OUTPUT_FILENAME = 'states_all.csv'
OUTPUT_EXTENDED_FILENAME = 'states_all_extended.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')

# Year range
yr_range = np.arange(1992, 2016, 1)


def main(logger=None, input_dir=None, output_dir=None):
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
    finance_data = pd.read_csv(os.path.join(input_dir, FINANCE_FILENAME))
    enroll_data = pd.read_csv(os.path.join(input_dir, ENROLL_EXTENDED_FILENAME))
    achieve_data = pd.read_csv(os.path.join(input_dir, ACHIEVE_FILENAME))

    all_data = finance_data.merge(enroll_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data = all_data.merge(achieve_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')

    all_data.sort_values(['YEAR', 'STATE'])

    output_path = os.path.join(output_dir, OUTPUT_EXTENDED_FILENAME)
    all_data.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
