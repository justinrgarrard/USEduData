"""
A script for compressing NCES enrollment data on states into a
single CSV file.
"""

import re
import zipfile
import os
import pandas as pd
import xlrd  # Support for older excel files, used by pd
import us  # US metadata, like state names
import shutil

# Disable warnings for Pandas dataframe assignments
pd.options.mode.chained_assignment = None  # default='warn'

# The name of the input CSV
INPUT_FILENAME = 'enroll_states.csv'

# The name of the output CSVs
OUTPUT_FILENAME = 'enroll_states_summary.csv'

# Summary columns mapping from specific to human-readable
SUMMARY_COLUMNS = {'PK_A_A': 'GRADES_PK_G',
                   'KG_A_A': 'GRADES_KG_G',
                   'G04_A_A': 'GRADES_4_G',
                   'G08_A_A': 'GRADES_8_G',
                   'G12_A_A': 'GRADES_12_G',
                   'G01-G08_A_A': 'GRADES_1_8_G',
                   'G09-G12_A_A': 'GRADES_9_12_G',
                   'A_A_A': 'GRADES_ALL_G'}

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')
surveyyear = re.compile(r'\d\d\d\d')


def find_specs(col_name):
    """
    Parses a column name for attributes and returns them.

    :param col_name:
    :return:[YEAR, GRADE, RACE, GENDER]
    """
    # Input in the form of YEAR_GRADE_RACE_GENDER
    spec_list = col_name.split('_')
    return spec_list


def summarize_enroll_data(input_df):
    """
    Summarize enrollment data to a few specific columns.

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


def main(logger=None, input_dir=None, output_dir=None):
    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))
    print(input_data)

    # Transform the data (YEAR_STATE format)
    output_df = summarize_enroll_data(input_data)
    print(output_df)

    # Output as file
    output_data_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output_df.to_csv(output_data_path, index=False)


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
