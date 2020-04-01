"""
A script for compressing NAEP (National Assessment of Educational Progress)
data on states into a single CSV file.
"""

import re
import zipfile
import os
import numpy as np
import pandas as pd
import xlrd  # Support for older excel files, used by pd
import us  # US metadata, like state names
import data_sanity_check


# The name of the input CSV
INPUT_FILENAME = 'naep_states_raw.csv'

# The name of the output CSV
OUTPUT_FILENAME = 'naep_states.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def naep_summarize_dataframe(naep_df):
    """

    :param naep_df:
    :return:
    """
    # Replace '—' with NaN's
    naep_df.replace('—', np.nan, inplace=True)

    # Convert entries into an easy-to-join format
    summary_df = pd.DataFrame()

    # Cast appropriate columns to strings
    naep_df['TEST_YEAR'] = naep_df['TEST_YEAR'].astype('str')

    # Basic info
    summary_df['STATE'] = naep_df['STATE']
    summary_df['YEAR'] = naep_df['YEAR']
    summary_df['DEMO'] = naep_df['DEMO']

    # We only want one of these per every test
    # summary_df['STATE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
    #                               (naep_df['TEST_YEAR'].str.contains('4'))]['STATE']
    #
    # summary_df['YEAR'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
    #                              (naep_df['TEST_YEAR'].str.contains('4'))]['YEAR']

    # We want an entry for each subject/year combination
    summary_df['AVG_MATH_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    summary_df['AVG_MATH_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']

    summary_df['AVG_READING_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    summary_df['AVG_READING_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']
    # Cast appropriate columns to strings
    summary_df['YEAR'] = summary_df['YEAR'].astype('str')

    # Create primary key
    pk = summary_df['YEAR'] + '_' + summary_df['STATE'] + '_' + summary_df['DEMO']

    summary_df.insert(0, 'PRIMARY_KEY', pk)

    # Collapse rows with the same primary key into one row
    summary_df = summary_df.groupby(['PRIMARY_KEY', 'YEAR', 'DEMO']).sum()
    summary_df.reset_index(inplace=True)
    print(summary_df)

    return summary_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Parsing ' + str(INPUT_FILENAME) + '...')

    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))

    # Transform the data (YEAR_STATE format)
    output_df = naep_summarize_dataframe(input_data)

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
