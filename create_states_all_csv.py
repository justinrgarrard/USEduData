"""
A script for creating adding additional data to the states.csv file (such as
the NAEP data).
"""

import re
import numpy as np
import pandas as pd
import us  # US metadata, like state names

FINANCE_FILENAME = 'finance_states.csv'
ENROLL_FILENAME = 'enroll_states.csv'
ACHIEVE_FILENAME = 'naep_states.csv'

OUTPUT_FILENAME = 'states_all.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')

# Year range
yr_range = np.arange(1992, 2016, 1)


def main():
    # Notify user
    print('Creating aggregate file...')

    # Combine data
    finance_data = pd.read_csv(FINANCE_FILENAME)
    enroll_data = pd.read_csv(ENROLL_FILENAME)

    # full = pd.concat([finance_data, enroll_data], sort=False)
    # full = finance_data.join(enroll_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')
    full = finance_data.merge(enroll_data, on=['PRIMARY_KEY', 'STATE', 'YEAR'], how='outer')
    full.sort_values(['YEAR', 'STATE'])

    full.to_csv(OUTPUT_FILENAME, index=False)


if __name__ == '__main__':
    main()
