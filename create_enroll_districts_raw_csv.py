"""
A script for compressing NCES enrollment data on districts into a
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

# Disable warnings for Pandas dataframe assignments
pd.options.mode.chained_assignment = None  # default='warn'

# The name of the output CSVs
OUTPUT_FILENAME = 'enroll_districts_raw.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'NCES_ENROLL_DISTRICTS.zip'

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
    'grades 1-8': 'G01-G08',
    'grades 9-12': 'G09-G12',
    'grade 10': 'G10',
    'grade 11': 'G11',
    'grade 12': 'G12',
    'grade 1': 'G01',
    'grade 2': 'G02',
    'grade 3': 'G03',
    'grade 4': 'G04',
    'grade 5': 'G05',
    'grade 6': 'G06',
    'grade 7': 'G07',
    'grade 8': 'G08',
    'grade 9': 'G09'}

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

    if 'Agency Name' in label_str:
        return 'Agency Name'

    label_str = label_str.lower()

    # Survey Year
    year_str = 'Y?'
    match = surveyyear.search(label_str)
    if match:
        year_str = match.group(0)

    # Grade
    # Default to A for All
    grade_str = 'A'
    for key in grade_map.keys():
        if key in label_str:
            grade_str = grade_map[key]
            break

    # Race
    # Default to A for All
    race_str = 'A'
    for key in race_map.keys():
        if key in label_str:
            race_str = race_map[key]
            break

    # Gender
    # Default to A for All
    if 'female' in label_str:
        gender_str = 'F'
    elif 'male' in label_str:
        gender_str = 'M'
    else:
        gender_str = 'A'

    # Pull it all together
    return '{0}_{1}_{2}_{3}'.format(year_str, grade_str, race_str, gender_str)


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
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
            # Notify user
            logger.debug('Parsing ' + str(item) + '...')

            # Read in the input file, skipping the first six rows and last seven rows
            # This chops off the header and footer text
            df = pd.read_csv(item, skiprows=6, skipfooter=7, engine='python')

            # Fix the column headers
            df.rename(mapper=label_fixup, axis=1, inplace=True)
            # print(df)

            # Append it to the join list
            df_list.append(df)

    # Merge the dataframes
    output_df = pd.concat(df_list, axis=1)

    # Remove duplicates
    output_df = output_df.loc[:, ~output_df.columns.duplicated()]

    # Sort the column names
    column_names = output_df.columns.tolist()
    column_names = sorted(list(set(column_names)))

    # Place 'Agency Name' and 'State Name' as first two columns
    column_names.remove('State Name')
    column_names.insert(0, 'State Name')

    column_names.remove('Agency Name')
    column_names.insert(0, 'Agency Name')

    output_df = output_df[column_names]

    # Handle whitespace issues related to district names in source data
    output_df['Agency Name'] = output_df[['Agency Name']].applymap(lambda x: str(x).strip())
    output_df.drop_duplicates(subset='Agency Name', inplace=True)

    # Output as file
    output_data_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output_df.to_csv(output_data_path, index=False)

    # Sanity check
    data_sanity_check.main(logger, output_dir, sanity_dir, OUTPUT_FILENAME)

    # Clean up
    shutil.rmtree(ZIP_NAME.strip('.zip') + '/')


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
