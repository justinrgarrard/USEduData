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
gr = ['PK', 'KG', 'G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08', 'G09', 'G10', 'G11', 'G12', 'G13', 'UG', 'AE', 'AL']
race_mod = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
gender_mod = ['M', 'F']

# Grade, All Races and All Genders
for item in gr:
    SCHEMA.append(item)

# Race, All Grades and All Genders
for item in race_mod:
    SCHEMA.append(item)

# Race + Grade
for grade in base:
    for race in race_mod:
        column_name = race + grade
        SCHEMA.append(column_name)

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


def nces_spreadsheet_to_dataframe(filename, logger=None):
    """
    Converts an NCES data spreadsheet to a Pandas dataframe.

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: pd.DataFrame
    """

    # Give the user a heads-up
    logger.debug('Parsing ' + str(filename) + '...')

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

    # Replace spaces with underscore in state names
    data['STATE'] = data['STATE'].apply(lambda x: re.sub(' ', '_', x.strip()))

    # Drop empty rows
    data = data.dropna(how='all')
    data = data[data['STATE'] != 'NAN']

    # Get rid of trailing whitespace from all strings
    for column in data.columns:
        try:
            data[column] = data[column].map(lambda x: x.strip())
        except:
            pass

    # Cast appropriate columns to numbers, removing non-number symbols
    for column in data.columns:
        if 'STATE' not in column:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    # Create a primary key for ease of use
    primary_key_col = data['SURVYEAR'].astype(str) + '_' + data['STATE']
    data.insert(0, 'PRIMARY_KEY', primary_key_col)

    # Sort
    data.sort_values(['PRIMARY_KEY'], inplace=True)
    return data


# def enroll_summarize_dataframe(enroll_df):
#     """
#
#     :return:
#     """
#     # Translate the -1, -2, and M values to NaN's
#     enroll_df.replace(-1, np.nan, inplace=True)
#     enroll_df.replace(-2, np.nan, inplace=True)
#
#     # Create summary dataframe
#     summary_df = pd.DataFrame()
#
#     # Create summary columns for state and year
#     summary_df['PRIMARY_KEY'] = enroll_df['SURVYEAR'].astype(str) + '_' + enroll_df['STATE']
#     summary_df['STATE'] = enroll_df['STATE']
#     summary_df['YEAR'] = enroll_df['SURVYEAR']
#
#     # Create summary columns for grades
#     def create_summary_grades(prefix):
#         if len(prefix) == 0:
#             prefix = 'G'
#             summary_df['GRADES_PK_' + prefix] = enroll_df['PK']
#             summary_df['GRADES_KG_' + prefix] = enroll_df['KG']
#         else:
#             summary_df['GRADES_PK_' + prefix] = enroll_df[prefix + 'PK']
#             summary_df['GRADES_KG_' + prefix] = enroll_df[prefix + 'KG']
#
#         summary_df['GRADES_4_' + prefix] = enroll_df[prefix + '04']
#         summary_df['GRADES_8_' + prefix] = enroll_df[prefix + '08']
#         summary_df['GRADES_12_' + prefix] = enroll_df[prefix + '12']
#
#         summary_df['GRADES_1_8_' + prefix] = enroll_df[prefix + '01'] + enroll_df[prefix + '02'] + \
#                                    enroll_df[prefix + '03'] + enroll_df[prefix + '04'] + \
#                                    enroll_df[prefix + '05'] + enroll_df[prefix + '06'] + \
#                                    enroll_df[prefix + '07'] + enroll_df[prefix + '08']
#
#         summary_df['GRADES_9_12_' + prefix] = enroll_df[prefix + '09'] + enroll_df[prefix + '10'] + \
#                                     enroll_df[prefix + '11'] + enroll_df[prefix + '12']
#
#         summary_df['GRADES_ALL_' + prefix] = summary_df['GRADES_PK_' + prefix] + summary_df['GRADES_1_8_' + prefix] + \
#                                              summary_df['GRADES_9_12_' + prefix]
#
#     create_summary_grades('')
#
#     # for race in race_mod:
#     #     create_summary_grades(race)
#
#     # Sort
#     summary_df.sort_values(['YEAR', 'STATE'])
#
#     return summary_df


def enroll_summarize_dataframe(enroll_df):
    """

    :return:
    """
    # Translate the -1, -2, and M values to NaN's
    enroll_df.replace(-1, np.nan, inplace=True)
    enroll_df.replace(-2, np.nan, inplace=True)

    # Create summary dataframe
    summary_df = pd.DataFrame()

    # Create summary columns for state and year
    summary_df['PRIMARY_KEY'] = enroll_df['PRIMARY_KEY']
    summary_df['STATE'] = enroll_df['STATE']
    summary_df['YEAR'] = enroll_df['SURVYEAR']

    # Create summary columns for grades
    def create_summary_grades(prefix, suffix=''):
        """
        Create summary values by race (prefix) and gender (suffix).
        :param prefix:
        :param suffix:
        :return:
        """
        if len(prefix) == 0:
            prefix = 'G'
            summary_df['GRADES_PK_' + prefix] = enroll_df['PK']
            summary_df['GRADES_KG_' + prefix] = enroll_df['KG']
        else:
            summary_df['GRADES_PK_' + prefix + suffix] = enroll_df[prefix + 'PK' + suffix]
            summary_df['GRADES_KG_' + prefix + suffix] = enroll_df[prefix + 'KG' + suffix]

        summary_df['GRADES_4_' + prefix + suffix] = enroll_df[prefix + '04' + suffix]
        summary_df['GRADES_8_' + prefix + suffix] = enroll_df[prefix + '08' + suffix]
        summary_df['GRADES_12_' + prefix + suffix] = enroll_df[prefix + '12' + suffix]

        summary_df['GRADES_1_8_' + prefix + suffix] = enroll_df[prefix + '01' + suffix] + enroll_df[prefix + '02' + suffix] + \
                                   enroll_df[prefix + '03' + suffix] + enroll_df[prefix + '04' + suffix] + \
                                   enroll_df[prefix + '05' + suffix] + enroll_df[prefix + '06' + suffix] + \
                                   enroll_df[prefix + '07' + suffix] + enroll_df[prefix + '08' + suffix]

        summary_df['GRADES_9_12_' + prefix + suffix] = enroll_df[prefix + '09' + suffix] + enroll_df[prefix + '10' + suffix] + \
                                    enroll_df[prefix + '11' + suffix] + enroll_df[prefix + '12' + suffix]

        summary_df['GRADES_ALL_' + prefix + suffix] = summary_df['GRADES_PK_' + prefix + suffix] + summary_df['GRADES_1_8_' + prefix + suffix] + \
                                             summary_df['GRADES_9_12_' + prefix + suffix]

    def race_summary_fixup(prefix):
        """
        A schema change in 2009 removed race columns (i.e. 'AS')
        and introduced race-gender columns (i.e. 'ASF' and 'ASM').
        This function reaggregates the data in post-2009 spreadsheets
        to establish consistency.
        :param prefix:
        :return:
        """
        summary_cols = ['GRADES_PK_' + prefix,
                        'GRADES_KG_' + prefix,
                        'GRADES_4_' + prefix,
                        'GRADES_8_' + prefix,
                        'GRADES_12_' + prefix,
                        'GRADES_1_8_' + prefix,
                        'GRADES_9_12_' + prefix,
                        'GRADES_ALL_' + prefix]

        for col in summary_cols:
            # Aggregate of Male + Female counts
            y = summary_df[col + 'M'] + summary_df[col + 'F']

            # Change null rows into aggregates
            summary_df[col] = summary_df[col].fillna(y)

    # General summaries
    create_summary_grades('')

    # Race summaries
    for race in race_mod:
        create_summary_grades(race)

    # Race and gender summaries
    for race in race_mod:
        for gender in gender_mod:
            create_summary_grades(race, gender)

    # Fixup for race summaries post 2009, see function comments
    for race in race_mod:
        race_summary_fixup(race)


    # Sort
    summary_df.sort_values(['PRIMARY_KEY'])

    return summary_df


def main(logger=None):
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
            df = nces_spreadsheet_to_dataframe(item, logger=logger)
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
