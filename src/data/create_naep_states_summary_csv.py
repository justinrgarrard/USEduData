"""
A script for compressing NAEP (National Assessment of Educational Progress)
data on states into a single CSV file.
"""

import re
import os
import pandas as pd
import us  # US metadata, like state names
from src.data import data_sanity_check

# The name of the input CSV
INPUT_FILENAME = 'naep_states.csv'

# The name of the output CSV
OUTPUT_FILENAME = 'naep_states_summary.csv'

# Summary columns mapping from specific to human-readable
SUMMARY_COLUMNS = {'G04_A_A_MATHEMATICS': 'AVG_MATH_4_SCORE',
                   'G08_A_A_MATHEMATICS': 'AVG_MATH_8_SCORE',
                   'G04_A_A_READING': 'AVG_READING_4_SCORE',
                   'G08_A_A_READING': 'AVG_READING_8_SCORE'}

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


def naep_summarize(input_df):
    """

    :param input_df:
    :return:
    """
    # Build the common columns
    output_df = pd.DataFrame()
    output_df['PRIMARY_KEY'] = input_df['PRIMARY_KEY']
    output_df['STATE'] = input_df['STATE']
    output_df['YEAR'] = input_df['YEAR']

    # Build the renamed columns
    for col in SUMMARY_COLUMNS.keys():
        new_name = SUMMARY_COLUMNS[col]
        output_df[new_name] = input_df[col]

    return output_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Parsing ' + str(INPUT_FILENAME) + '...')

    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))

    # Summarize the data
    output_df = naep_summarize(input_data)

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
