"""
A script for creating adding additional data to the states.csv file (such as
the NAEP data).
"""

import re
import numpy as np
import pandas as pd
import us  # US metadata, like state names

INPUT_FILENAME = 'finance_states.csv'
INPUT_FILENAME_2 = 'naep_states.csv'

OUTPUT_FILENAME = 'states_plus.csv'

# Schema of the states.csv file
STATES_SCHEMA = ['STATE',
                 'YEAR',
                 'ENROLL',
                 'TOTAL_REVENUE',
                 'FEDERAL_REVENUE',
                 'STATE_REVENUE',
                 'LOCAL_REVENUE',
                 'TOTAL_EXPENDITURE',
                 'INSTRUCTION_EXPENDITURE',
                 'SUPPORT_SERVICES_EXPENDITURE',
                 'OTHER_EXPENDITURE',
                 'CAPITAL_OUTLAY_EXPENDITURE']

# Schema used for the NAEP data files
NDE_SCHEMA = ['YEAR',
              'STATE',
              'DEMO',
              'AVERAGE_SCORE',
              'TEST_SUBJECT',
              'TEST_YEAR']

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')

# Year range
yr_range = np.arange(1992, 2016, 1)


def main():
    # Load data into dataframes
    states_data = pd.read_csv(INPUT_FILENAME)
    naep_data = pd.read_csv(INPUT_FILENAME_2)

    states_data['INDEX'] = states_data.apply(lambda x: x['STATE'] + str(x['YEAR']), axis=1)
    naep_data['INDEX'] = naep_data.apply(lambda x: x['STATE'] + str(x['YEAR']), axis=1)

    naep_data_math = naep_data.loc[naep_data['TEST_SUBJECT'] == 'Mathematics']
    naep_data_reading = naep_data.loc[naep_data['TEST_SUBJECT'] == 'Reading']

    naep_data_math_4 = naep_data_math.loc[naep_data_math['TEST_YEAR'] == 4]
    naep_data_math_8 = naep_data_math.loc[naep_data_math['TEST_YEAR'] == 8]
    naep_data_reading_4 = naep_data_reading.loc[naep_data_reading['TEST_YEAR'] == 4]
    naep_data_reading_8 = naep_data_reading.loc[naep_data_reading['TEST_YEAR'] == 8]

    # Fill in missing rows with averages
    for i in yr_range:
        if neap_data_math_4.where()

    # Perform joins
    def joiner(x):
        if naep_data_math_4['INDEX'].str.contains(x):
            return naep_data_math_4.loc[naep_data_math_4['INDEX' == x]]
        else:
            return None
    # states_data['MATH_SCORE_4'] = naep_data_math_4.loc[
    # (naep_data_math_4['YEAR'] == states_data['YEAR']) & (naep_data_math_4['STATE'] == states_data['STATE'])]
    # g = pd.concat([states_data, naep_data_math_4], sort=False)
    # g = states_data.join(naep_data_math_4, on=['YEAR', 'STATE'], how='outer')

    states_data['MATH_SCORE_4'] = states_data['INDEX'].apply(joiner)

    # Write to file as CSV
    # g.to_csv(OUTPUT_FILENAME, index=False)
    states_data.to_csv(OUTPUT_FILENAME, index=False)


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
