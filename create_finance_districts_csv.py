"""
A script for compressing U.S. Census financial data on school districts into a
single CSV file.
"""

import re
import zipfile
import os
import pandas as pd
import xlrd  # Support for older excel files, used by pd
import us  # US metadata, like state names
import shutil
import data_sanity_check

# The name of the output CSV
OUTPUT_FILENAME = 'finance_districts.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'US_CENSUS_FINANCE.zip'

# A hard-coded schema that matches the column structure
# Can be modified to include additional columns
SCHEMA = ['STATE',
          'ENROLL',
          'NAME',
          'YRDATA',
          'TOTALREV',
          'TFEDREV',
          'TSTREV',
          'TLOCREV',
          'TOTALEXP',
          'TCURINST',
          'TCURSSVC',
          'TCURONON',
          'TCAPOUT']

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def elsect_spreadsheet_to_dataframe(filename, logger=None):
    """
    Converts a elsect data spreadsheet to a Pandas dataframe.
    Performs minor alterations to the data
    (i.e. changing '1' to 'Alabama').

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: pd.DataFrame
    """

    # Give the user a heads-up
    logger.debug('Parsing ' + str(filename) + '...')

    # Convert the year data to full years
    # Can't depend on spreadsheet value, so we'll do it by filename
    year = int(re.findall(numbersonly, filename)[0])
    if year < 10:
        year = '200' + str(year)
    elif year < 50:
        year = '20' + str(year)
    else:
        year = '19' + str(year)

    # Use year to determine state identifier
    # (column name changes in 2002)
    if int(year) >= 2002:
        st_code = ['IDCENSUS']
    elif int(year) == 1992:
        st_code = ['ID']
    else:
        st_code = ['GOVSID']
    specific_schema = st_code + SCHEMA

    # Open the file, parse it, and truncate the highlights
    data = pd.read_excel(filename, sheet_name=0, dtype=str)
    data = pd.DataFrame(data, columns=specific_schema)

    # Convert the state codes to state names
    data[st_code] = data[st_code].applymap(lambda x: x[:2])
    data['STATE'] = data[st_code].applymap(lambda x: us.STATES[int(x) - 1])
    data['STATE'] = data['STATE'].apply(lambda x: str(x).upper())
    data = data.drop(st_code, axis=1)

    # Replace spaces with underscore in state names
    data['STATE'] = data['STATE'].apply(lambda x: re.sub(' ', '_', str(x).strip()))

    # Fill in the year data
    data['YRDATA'] = year

    return data


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Unpack the data
    input_data_path = os.path.join(input_dir, ZIP_NAME)
    input_data = zipfile.ZipFile(input_data_path, 'r')
    file_list = input_data.namelist()
    file_list.remove(ZIP_NAME.strip('.zip')+'/')
    input_data.extractall(os.getcwd())
    input_data.close()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        df = elsect_spreadsheet_to_dataframe(item, logger)
        record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Write to file as CSV
    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output.to_csv(output_path, index=False)

    # Sanity check
    data_sanity_check.main(logger, output_dir, sanity_dir, OUTPUT_FILENAME, year_label='YRDATA')

    # Clean up
    shutil.rmtree(ZIP_NAME.strip('.zip') + '/')


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
