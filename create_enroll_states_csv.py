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

# The name of the output CSVs
OUTPUT_FILENAME_BASE = 'enroll_states_base.csv'
OUTPUT_FILENAME = 'enroll_states.csv'
OUTPUT_FILENAME_EXTENDED = 'enroll_states_extended.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'NCES_ENROLL_STATES.zip'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')
surveyyear = re.compile(r'\d\d\d\d')

# Column names used for generating the schema
# Maybe replace these with a few fancy regexes?
grade_map = {
    'prekindergarten': 'PK',
    'kindergarten': 'KG',
    'grade 1': 'G01',
    'grade 2': 'G02',
    'grade 3': 'G03',
    'grade 4': 'G04',
    'grade 5': 'G05',
    'grade 6': 'G06',
    'grade 7': 'G07',
    'grade 8': 'G08',
    'grade 9': 'G09',
    'grade 10': 'G10',
    'grade 11': 'G11',
    'grade 12': 'G12'}

race_map = {
    'indian': 'AM',
    'asian': 'AS',
    'hispanic': 'HI',
    'black': 'BL',
    'white': 'WH',
    'hawaiian': 'HP',
    'two or more': 'TR'}


def label_fixup(label_str):
    """
    Simplifies NCES column labels to a more user-friendly format.

    :param label_str:
    :return:
    """
    if 'State Name' in label_str:
        return 'State Name'

    label_str = label_str.lower()
    # print(label_str)

    # Survey Year
    year_str = 'Y?'
    match = surveyyear.search(label_str)
    if match:
        year_str = match.group(0)

    # Grade
    grade_str = 'G?'
    for key in grade_map.keys():
        if key in label_str:
            grade_str = grade_map[key]
            break

    # Race
    race_str = 'R?'
    for key in race_map.keys():
        if key in label_str:
            race_str = race_map[key]
            break

    # Gender
    if 'female' in label_str:
        gender_str = 'F'
    elif 'male' in label_str:
        gender_str = 'M'
    else:
        gender_str = 'S?'

    # Pull it all together
    # print('{0}_{1}_{2}_{3}'.format(year_str, grade_str, race_str, gender_str))
    return '{0}_{1}_{2}_{3}'.format(year_str, grade_str, race_str, gender_str)


def main(logger=None, input_dir=None, output_dir=None):
    # Unpack the data
    input_data_path = os.path.join(input_dir, ZIP_NAME)
    input_data = zipfile.ZipFile(input_data_path, 'r')
    file_list = input_data.namelist()
    file_list.remove(ZIP_NAME.strip('.zip') + '/')
    input_data.extractall(os.getcwd())
    input_data.close()

    # Combine the data into a single dataframe
    df_list = []
    for item in file_list:
        if '/.' not in item:
            # Read in the input file, skipping the first six rows and last seven rows
            # This chops off the unnecessary header and footer
            df = pd.read_csv(item, skiprows=6, skipfooter=7, engine='python')

            # Fix the column headers
            df.rename(mapper=label_fixup, axis=1, inplace=True)
            print(df)

            # Append it to the join list
            df_list.append(df)

    # output_df = pd.concat(df_list)
    # print(output_df)

    # Clean up
    shutil.rmtree(ZIP_NAME.strip('.zip') + '/')


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
