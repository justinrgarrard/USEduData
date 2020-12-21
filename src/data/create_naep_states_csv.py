"""
A script for compressing NAEP (National Assessment of Educational Progress)
data on states into a single CSV file.
"""

import re
import os
import numpy as np
import pandas as pd
import us  # US metadata, like state names
from src.data import data_sanity_check

# The name of the input CSV
INPUT_FILENAME = 'naep_states_raw.csv'

# The name of the output CSV
OUTPUT_FILENAME = 'naep_states.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def find_specs(col_name):
    """
    Parses a column name for attributes and returns them.

    :param col_name:
    :return:[YEAR, GRADE, RACE, GENDER]
    """
    # Input in the form of YEAR_GRADE_RACE_GENDER
    spec_list = col_name.split('_')
    return spec_list


def naep_aggregate(input_df):
    """

    :param input_df:
    :return:
    """
    # Treat years as strings
    input_df['YEAR'] = input_df['YEAR'].astype('str')
    # input_df.drop_duplicates(inplace=True)

    # PRIMARY_KEY, STATE, and YEAR will be the same
    staging_df = pd.DataFrame()
    staging_df['PRIMARY_KEY'] = input_df['YEAR'] + '_' + input_df['STATE']
    staging_df['STATE'] = input_df['STATE']
    staging_df['YEAR'] = input_df['YEAR']

    # Map DEMO column to a set of columns
    demographics = input_df['DEMO'].unique().tolist()
    subjects = input_df['TEST_SUBJECT'].unique().tolist()

    data_cols = []
    for demo in demographics:
        for subject in subjects:
            new_col_name = demo + '_' + subject.upper()
            data_cols.append(new_col_name)
            staging_df[new_col_name] = pd.Series()

    # Populate the output dataframe using the input dataframe
    # There has to be a nicer way to do this...
    for col_name in data_cols:
        # Parse the column name
        specs = find_specs(col_name)
        grade = specs[0]
        race = specs[1]
        gender = specs[2]
        test_subject = specs[3]
        demo = grade + '_' + race + '_' + gender

        input_data = input_df[(input_df['DEMO'].str.match(demo))
                              & (input_df['TEST_SUBJECT'].str.match(test_subject, case=False))][['STATE', 'YEAR', 'AVG_SCORE']]
        input_data.rename(columns={'STATE': 'STATE', 'YEAR': 'YEAR', 'AVG_SCORE': col_name}, inplace=True)

        target_col = '{0}_{1}_{2}_{3}'.format(grade, race, gender, test_subject)
        target_data = staging_df[['STATE', 'YEAR', target_col]]

        target_data[col_name] = input_data[col_name]
        staging_df[target_col].update(target_data[col_name])

    # Combine rows with the same primary key
    output_df = staging_df.groupby(by=['PRIMARY_KEY', 'STATE', 'YEAR']).sum()
    output_df = output_df.reset_index()

    # Replace 0's with NaN
    output_df = output_df.replace(0, np.nan)

    return output_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Parsing ' + str(INPUT_FILENAME) + '...')

    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))

    # Aggregate the data (combine rows per demographic)
    output_df = naep_aggregate(input_data)

    # Output as file
    output_data_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output_df.to_csv(output_data_path, index=False)

    # Sanity check
    data_sanity_check.main(logger, output_dir, sanity_dir, OUTPUT_FILENAME, count_year_nulls=True)


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
