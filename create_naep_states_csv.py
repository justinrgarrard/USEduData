"""
A script for compressing NAEP (National Assessment of Educational Progress)
data on states into a single CSV file.
"""

import re
import zipfile
import os
import pandas as pd
import xlrd  # Support for older excel files, used by pd
import us  # US metadata, like state names


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


def nde_spreadsheet_to_dataframe(filename):
    """
    Converts an NDE data spreadsheet to a Pandas dataframe.

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: dict
    """

    # Give the user a heads-up
    print('Parsing ' + str(filename) + '...')


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

    # Drop the unused demographic column
    data = data.drop('DEMO', axis=1)

    return data


def main():
    # Unpack the data
    out = zipfile.ZipFile(ZIP_NAME, 'r')
    file_list = out.namelist()
    out.extractall(os.getcwd())
    out.close()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        df = nde_spreadsheet_to_dataframe(item)
        record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Write to file as CSV
    output.to_csv(OUTPUT_FILENAME, index=False)

    # Clean up
    for item in file_list:
        os.remove(item)


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
