"""
A script for compressing NCES enrollment data on states into a
single CSV file.
"""

import re
import zipfile
import os
import numpy as np
import pandas as pd
import xlrd  # Support for older excel files, used by pd
import us  # US metadata, like state names
import shutil

# Disable warnings for Pandas dataframe assignments
pd.options.mode.chained_assignment = None  # default='warn'

# The name of the output CSVs
OUTPUT_FILENAME_BASE = 'enroll_states_base.csv'
OUTPUT_FILENAME = 'enroll_states.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'nces_enroll.zip'

# A schema that matches the column structure
# Can be modified to include additional columns
SCHEMA = ['SURVYEAR',
          'STATENAME',
          'STNAME',
          'STATE',
          'TOTAL',
          'MEMBER']

# It would've been annoying to hard code each variation, so let's do it this way
base = ['PK', 'KG', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', 'UG', 'AE', 'AL']
race_mod = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
gender_mod = ['M', 'F']

# Grade, All Races and All Genders
gr = ['PK', 'KG', 'G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08', 'G09', 'G10', 'G11', 'G12', 'G13', 'UG', 'AE', 'AL']
for item in gr:
    SCHEMA.append(item)

# Race, All Grades and All Genders
for item in race_mod:
    SCHEMA.append(item)

# Race + Grade + Gender
for grade in base:
    for race in race_mod:
        for gender in gender_mod:
            column_name = race + grade + gender
            SCHEMA.append(column_name)

SCHEMA = list(set(SCHEMA))
SCHEMA.sort()

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')


def nces_spreadsheet_to_dataframe(filename):
    """
    Converts an NCES data spreadsheet to a Pandas dataframe.

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: pd.DataFrame
    """

    # Give the user a heads-up
    print('Parsing ' + str(filename) + '...')

    # Open the file, parse it, and truncate the highlights
    # print(SCHEMA)
    d = pd.read_excel(filename, sheet_name=0, dtype=str)

    # Fixup for whitespace in column names
    d.rename(columns=lambda x: x.strip(), inplace=True)

    for column in SCHEMA:
        if column not in d.columns:
            d[column] = np.nan

    data = d[SCHEMA]

    # Add a year, because the source spreadsheets are unreliable
    data['SURVYEAR'] = re.findall(numbersonly, filename)[0]

    # Synonymous columns fixup
    if data['STATE'].isnull().values.any():
        if data['STATENAME'].isnull().values.any():
            data['STATE'] = data['STNAME']
        else:
            data['STATE'] = data['STATENAME']
    data.drop(['STNAME', 'STATENAME'], axis=1)

    if True in data['TOTAL'].isnull():
        data['TOTAL'] = data['MEMBER']
    data.drop('MEMBER', axis=1)

    # Some years only used abbreviations for states
    # Change those to full state names
    if 'AZ' in data['STATE'].values:
        abbr_to_name = us.states.mapping('abbr', 'name')
        for key in abbr_to_name.keys():
            abbr_to_name[key] = abbr_to_name[key].upper()
        data['STATE'].replace(abbr_to_name, inplace=True)

    # Capitalize state names if necessary
    data['STATE'] = data['STATE'].apply(lambda x: x.upper())

    # Drop empty rows
    data = data.dropna(how='all')

    # Get rid of trailing whitespace from all strings
    for column in data.columns:
        try:
            data[column] = data[column].map(lambda x: x.strip())
        except:
            pass

    # Sort
    data.sort_values(['SURVYEAR', 'STATE'])

    return data


def enroll_summarize_dataframe(enroll_df):
    """

    :return:
    """
    # Translate the -1, -2, and M values to NaN's
    enroll_df.replace(-1, np.nan, inplace=True)
    enroll_df.replace(-2, np.nan, inplace=True)
    enroll_df.replace('-1', np.nan, inplace=True)
    enroll_df.replace('-2', np.nan, inplace=True)
    enroll_df.replace('M', np.nan, inplace=True)

    # Create summary dataframe
    summary_df = pd.DataFrame()

    # Create summary columns for state and year
    summary_df['PRIMARY_KEY'] = enroll_df['SURVYEAR'] + '_' + enroll_df['STATE']
    summary_df['STATE'] = enroll_df['STATE']
    summary_df['YEAR'] = enroll_df['SURVYEAR']

    # Create summary columns for grades
    summary_df['GRADES_PK'] = pd.to_numeric(enroll_df['PK'], errors='coerce')
    summary_df['GRADES_KG'] = pd.to_numeric(enroll_df['KG'], errors='coerce')
    summary_df['GRADES_4'] = pd.to_numeric(enroll_df['G04'], errors='coerce')
    summary_df['GRADES_8'] = pd.to_numeric(enroll_df['G08'], errors='coerce')
    summary_df['GRADES_12'] = pd.to_numeric(enroll_df['G12'], errors='coerce')

    summary_df['GRADES_1_8'] = pd.to_numeric(enroll_df['G01'], errors='coerce') + pd.to_numeric(enroll_df['G02'], errors='coerce') + \
                            pd.to_numeric(enroll_df['G03'], errors='coerce') + pd.to_numeric(enroll_df['G04'], errors='coerce') + \
                            pd.to_numeric(enroll_df['G05'], errors='coerce') + pd.to_numeric(enroll_df['G06'], errors='coerce') + \
                               pd.to_numeric(enroll_df['G07'], errors='coerce') + pd.to_numeric(enroll_df['G08'], errors='coerce')

    summary_df['GRADES_9_12'] = pd.to_numeric(enroll_df['G09'], errors='coerce') + pd.to_numeric(enroll_df['G10'], errors='coerce') + \
                                pd.to_numeric(enroll_df['G11'], errors='coerce') + pd.to_numeric(enroll_df['G12'], errors='coerce')

    summary_df['GRADES_KG_12'] = pd.to_numeric(summary_df['GRADES_PK'], errors='coerce') + summary_df['GRADES_1_8'] + summary_df['GRADES_9_12']

    # Sort
    summary_df.sort_values(['YEAR', 'STATE'])

    return summary_df


def main():
    # target = 'enroll_2014.xls'
    # df = nces_spreadsheet_to_dataframe(target)
    # df.to_csv(OUTPUT_FILENAME, index=False)
    #
    # print(df['STATE'].isnull())

    # Unpack the data
    out = zipfile.ZipFile(ZIP_NAME, 'r')
    file_list = out.namelist()
    file_list.remove(ZIP_NAME.strip('.zip') + '/')
    out.extractall(os.getcwd())
    out.close()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        if '/.' not in item:
            df = nces_spreadsheet_to_dataframe(item)
            record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Drop any empty columns
    output = output.dropna(how='all', axis=1)

    # Write to file as CSV
    output.to_csv(OUTPUT_FILENAME_BASE, index=False)

    # Summarize the output
    output = enroll_summarize_dataframe(output)
    output.to_csv(OUTPUT_FILENAME, index=False)

    # Clean up
    shutil.rmtree(ZIP_NAME.strip('.zip') + '/')


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
