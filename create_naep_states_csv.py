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


OUTPUT_FILENAME_BASE = 'naep_states_base.csv'
OUTPUT_FILENAME = 'naep_states.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'NDE.zip'

# Schema used for the NAEP data files
NDE_SCHEMA = ['YEAR',
              'STATE',
              'DEMO',
              'AVERAGE_SCORE']

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def nde_spreadsheet_to_dataframe(filename, logger=None):
    """
    Converts an NDE data spreadsheet to a Pandas dataframe.

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: dict
    """

    # Give the user a heads-up
    logger.debug('Parsing ' + str(filename) + '...')

    # Open the file, parse it, and truncate the highlights
    data = pd.read_excel(filename, sheet_name=1, dtype=str)
    data = data.rename(index=str, columns={'Year': 'YEAR',
                                           'Jurisdiction': 'STATE',
                                           'All students': 'DEMO',
                                           'Average scale score': 'AVG_SCORE'})
    data['TEST_SUBJECT'] = filename.split('_')[1]
    data['TEST_YEAR'] = filename.split('_')[2].strip('.Xls')

    # Clean up the year by removing the superscript
    data['YEAR'] = data['YEAR'].apply(lambda x: x[:4])

    # Capitalize state names if necessary
    data['STATE'] = data['STATE'].apply(lambda x: x.upper())

    # Replace spaces with underscore in state names
    data['STATE'] = data['STATE'].apply(lambda x: re.sub(' ', '_', x.strip()))

    # Drop the unused demographic column
    data = data.drop('DEMO', axis=1)

    # Cast appropriate columns to numbers, removing non-number symbols
    for column in data.columns:
        if column not in ['STATE', 'YEAR', 'TEST_SUBJECT', 'TEST_YEAR']:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    return data


def naep_summarize_dataframe(naep_df):
    """

    :param naep_df:
    :return:
    """
    # Replace '—' with NaN's
    naep_df.replace('—', np.nan, inplace=True)

    # Convert entries into an easy-to-join format
    summary_df = pd.DataFrame()

    # We only want one of these per every test
    summary_df['STATE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                  (naep_df['TEST_YEAR'].str.contains('4'))]['STATE']

    summary_df['YEAR'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                 (naep_df['TEST_YEAR'].str.contains('4'))]['YEAR']

    # We want an entry for each subject/year combination
    summary_df['AVG_MATH_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    summary_df['AVG_MATH_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Mathematics')) &
                                             (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']

    summary_df['AVG_READING_4_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('4'))]['AVG_SCORE']

    summary_df['AVG_READING_8_SCORE'] = naep_df[(naep_df['TEST_SUBJECT'].str.contains('Reading')) &
                                                (naep_df['TEST_YEAR'].str.contains('8'))]['AVG_SCORE']

    pk = summary_df['YEAR'] + '_' + summary_df['STATE']

    summary_df.insert(0, 'PRIMARY_KEY', pk)

    return summary_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Unpack the data
    input_data_path = os.path.join(input_dir, ZIP_NAME)
    input_data = zipfile.ZipFile(input_data_path, 'r')
    file_list = input_data.namelist()
    input_data.extractall(os.getcwd())
    input_data.close()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        df = nde_spreadsheet_to_dataframe(item, logger)
        record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Write base data to file as CSV
    output_path = os.path.join(output_dir, OUTPUT_FILENAME_BASE)
    output.to_csv(output_path, index=False)

    # Write summary data to file as CSV
    output = naep_summarize_dataframe(output)
    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output.to_csv(output_path, index=False)

    # Clean up
    for item in file_list:
        os.remove(item)

    # Sanity check
    data_sanity_check.main(logger, output_dir, sanity_dir, OUTPUT_FILENAME, count_year_nulls=True)


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
