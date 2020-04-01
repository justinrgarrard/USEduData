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
STAGING_FILENAME = 'naep_states_aggregate_staging.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def naep_aggregate(naep_df):
    """
    Aggregates NAEP data by demographic and test subject.

    :param naep_df:
    :return:
    """
    # Replace '—' with NaN's
    naep_df.replace('—', np.nan, inplace=True)

    # Convert entries into an easy-to-join format
    aggregate_df = pd.DataFrame()

    # Cast appropriate columns to strings
    naep_df['TEST_YEAR'] = naep_df['TEST_YEAR'].astype('str')

    # Basic info
    aggregate_df['STATE'] = naep_df['STATE']
    aggregate_df['YEAR'] = naep_df['YEAR']
    aggregate_df['DEMO'] = naep_df['DEMO']

    # We want an entry for each subject/year combination
    aggregate_df['AVG_MATH_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    aggregate_df['AVG_MATH_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']

    aggregate_df['AVG_READING_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    aggregate_df['AVG_READING_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']
    # Cast appropriate columns to strings
    aggregate_df['YEAR'] = aggregate_df['YEAR'].astype('str')

    # Create primary key
    pk = aggregate_df['YEAR'] + '_' + aggregate_df['STATE'] + '_' + aggregate_df['DEMO']

    aggregate_df.insert(0, 'PRIMARY_KEY', pk)

    # Collapse rows with the same primary key into one row
    aggregate_df = aggregate_df.groupby(['PRIMARY_KEY', 'STATE', 'YEAR', 'DEMO']).sum()
    aggregate_df.reset_index(inplace=True)
    print(aggregate_df)

    # Reduce primary key (year_state)
    aggregate_df['PRIMARY_KEY'] = aggregate_df['YEAR'] + '_' + aggregate_df['STATE']

    return aggregate_df


def naep_format(aggregate_df):
    """
    Formats NAEP data by year_state.

    :param aggregate_df:
    :return:
    """
    return aggregate_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Parsing ' + str(INPUT_FILENAME) + '...')

    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))

    # Aggregate the data (combine rows per demographic)
    aggregate_df = naep_aggregate(input_data)

    # Output as file
    staging_data_path = os.path.join(output_dir, STAGING_FILENAME)
    aggregate_df.to_csv(staging_data_path, index=False)

    # Format the data (YEAR_STATE format)
    output_df = naep_format(aggregate_df)

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
