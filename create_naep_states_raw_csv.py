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

OUTPUT_FILENAME = 'naep_states_raw.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'NAEP_ASSESS_STATES.zip'

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
    data = pd.read_excel(filename, dtype=str, skiprows=8, skipfooter=7)
    data = data.rename(index=str, columns={'Year': 'YEAR',
                                           'Jurisdiction': 'STATE',
                                           'All students': 'DEMO',
                                           'Gender': 'DEMO',
                                           'Status as English Language Learner, 2 categories': 'DEMO',
                                           'Race/ethnicity used to report trends, school-reported': 'DEMO',
                                           'Race/ethnicity using 2011 guidelines, school-reported': 'DEMO',
                                           'Average scale score': 'AVG_SCORE'})
    filename = filename.split('/')[1]
    data['TEST_SUBJECT'] = filename.split('_')[1]
    data['TEST_YEAR'] = filename.split('_')[2].replace('G', '')

    # Clean up the year by removing the superscript
    data['YEAR'] = data['YEAR'].apply(lambda x: x[:4])

    # Capitalize state names if necessary
    data['STATE'] = data['STATE'].apply(lambda x: x.upper())

    # Replace spaces with underscore in state names
    data['STATE'] = data['STATE'].apply(lambda x: re.sub(' ', '_', x.strip()))

    # Drop the unused demographic column
    # data = data.drop('DEMO', axis=1)

    # Cast appropriate columns to numbers, removing non-number symbols
    data['AVG_SCORE'] = pd.to_numeric(data['AVG_SCORE'], errors='coerce')

    return data


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Unpack the data
    input_data_path = os.path.join(input_dir, ZIP_NAME)
    input_data = zipfile.ZipFile(input_data_path, 'r')
    file_list = input_data.namelist()
    file_list.remove(ZIP_NAME.strip('.zip') + '/')
    input_data.extractall(os.getcwd())
    input_data.close()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        df = nde_spreadsheet_to_dataframe(item, logger)
        record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Output as file
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
