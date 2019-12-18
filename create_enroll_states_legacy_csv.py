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
OUTPUT_FILENAME_EXTENDED = 'enroll_states_extended.csv'

# The name of the zip file being unpacked
ZIP_NAME = 'nces_enroll.zip'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')

# Column names used for generating the schema
base = ['PK', 'KG', '01', '02', '03', '04', '05', '06', '07', '08', '09',
        '10', '11', '12', '13', 'UG', 'AE', 'AL']
gr = ['PK', 'KG', 'G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08',
         'G09', 'G10', 'G11', 'G12', 'G13', 'UG', 'AE', 'AL']
race_mod = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
gender_mod = ['M', 'F']


def gen_schema():
    """
    A function that creates extends the schema with columns
    appropriate to the enrollment data.
    :return: SCHEMA
    :rtype list
    """
    schema = ['SURVYEAR',
              'STATENAME',
              'STNAME',
              'STATE',
              'TOTAL',
              'MEMBER']

    # Grade, All Races and All Genders
    for item in gr:
        schema.append(item)

    # Race, All Grades and All Genders
    for item in race_mod:
        schema.append(item)

    # Race + Grade
    for grade in base:
        for race in race_mod:
            column_name = race + grade
            schema.append(column_name)

    # Race + Grade + Gender
    for grade in base:
        for race in race_mod:
            for gender in gender_mod:
                column_name = race + grade + gender
                schema.append(column_name)

    schema = list(set(schema))
    schema.sort()

    return schema


def nces_spreadsheet_to_dataframe(filename, schema, logger=None):
    """
    Converts an NCES data spreadsheet to a Pandas dataframe.
    Performs several cleaning operations to format the input data.

    :param filename: The name of the xls file.
    :return: A dictionary with the U.S. states as keys.
    :rtype: pd.DataFrame
    """

    # Give the user a heads-up
    logger.debug('Parsing ' + str(filename) + '...')

    # Parse the input file
    data = pd.read_excel(filename, sheet_name=0, dtype=str)

    def state_name_fixups():
        """
        Fixes for standardizing state names in input data.
        :return:
        """
        # Standardize 'state name' column name
        if data['STATE'].isnull().values.any():
            if data['STATENAME'].isnull().values.any():
                data['STATE'] = data['STNAME']
            else:
                data['STATE'] = data['STATENAME']
        data.drop(['STNAME', 'STATENAME'], axis=1)
        data['STATE'] = data['STATE'].astype(str)

        # Replace state abbreviations with full name
        if 'AZ' in data['STATE'].values:
            abbr_to_name = us.states.mapping('abbr', 'name')
            for key in abbr_to_name.keys():
                abbr_to_name[key] = abbr_to_name[key].upper()
            data['STATE'].replace(abbr_to_name, inplace=True)

        # Enforce consistent capitalization
        data['STATE'] = data['STATE'].apply(lambda x: x.upper())

        # Replace spaces with underscores
        data['STATE'] = data['STATE'].apply(lambda x: re.sub(' ', '_', x.strip()))

    # Fix whitespace in column names
    data.rename(columns=lambda x: x.strip(), inplace=True)
    for column in schema:
        if column not in data.columns:
            data[column] = np.nan
    data = data[schema]

    # Set the year using the filename
    data['SURVYEAR'] = re.findall(numbersonly, filename)[0]

    state_name_fixups()

    # Standardize 'total enrollment' column
    if True in data['TOTAL'].isnull():
        data['TOTAL'] = data['MEMBER']
    data.drop('MEMBER', axis=1)

    # Drop empty rows
    data = data.dropna(how='all')
    data = data[data['STATE'] != 'NAN']

    # Get rid of trailing whitespace from all columns
    for column in data.columns:
        try:
            data[column] = data[column].map(lambda x: x.strip())
        except:
            pass

    # Cast columns for numeric data, removing non-number symbols
    for column in data.columns:
        if 'STATE' not in column:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    # Create a primary key for ease of use
    primary_key_col = data['SURVYEAR'].astype(str) + '_' + data['STATE']
    data.insert(0, 'PRIMARY_KEY', primary_key_col)

    # Sort
    data.sort_values(['PRIMARY_KEY'], inplace=True)

    return data


def enroll_summarize_dataframe(enroll_df):
    """

    :return:
    """
    # Translate the -1 and -2 values to NaN's
    enroll_df.replace(-1, np.nan, inplace=True)
    enroll_df.replace(-2, np.nan, inplace=True)

    # Create summary dataframe
    summary_df = pd.DataFrame()

    # Create summary columns for state and year
    summary_df['PRIMARY_KEY'] = enroll_df['PRIMARY_KEY']
    summary_df['STATE'] = enroll_df['STATE']
    summary_df['YEAR'] = enroll_df['SURVYEAR']

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

        summary_df['GRADES_1_8_' + prefix + suffix] = enroll_df[prefix + '01' + suffix] + \
                                                      enroll_df[prefix + '02' + suffix] + \
                                                      enroll_df[prefix + '03' + suffix] + \
                                                      enroll_df[prefix + '04' + suffix] + \
                                                      enroll_df[prefix + '05' + suffix] + \
                                                      enroll_df[prefix + '06' + suffix] + \
                                                      enroll_df[prefix + '07' + suffix] + \
                                                      enroll_df[prefix + '08' + suffix]

        summary_df['GRADES_9_12_' + prefix + suffix] = enroll_df[prefix + '09' + suffix] + \
                                                       enroll_df[prefix + '10' + suffix] + \
                                                       enroll_df[prefix + '11' + suffix] + \
                                                       enroll_df[prefix + '12' + suffix]

        summary_df['GRADES_ALL_' + prefix + suffix] = summary_df['GRADES_PK_' + prefix + suffix] + \
                                                      summary_df['GRADES_1_8_' + prefix + suffix] + \
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
    simple_summary_df = summary_df.copy(deep=True)

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

    return simple_summary_df, summary_df


def main(logger=None, input_dir=None, output_dir=None):
    # Unpack the data
    input_data_path = os.path.join(input_dir, ZIP_NAME)
    input_data = zipfile.ZipFile(input_data_path, 'r')
    file_list = input_data.namelist()
    file_list.remove(ZIP_NAME.strip('.zip') + '/')
    input_data.extractall(os.getcwd())
    input_data.close()

    # Generate the schema
    schema = gen_schema()

    # Iterate through spreadsheets, extracting data
    record = []
    for item in file_list:
        if '/.' not in item:
            df = nces_spreadsheet_to_dataframe(item, schema, logger=logger)
            record.append(df)

    # Glue the annual surveys into a single file
    output = pd.concat(record)

    # Drop any empty columns
    output = output.dropna(how='all', axis=1)

    # Write base data to file as CSV
    output_base_data_path = os.path.join(output_dir, OUTPUT_FILENAME_BASE)
    output.to_csv(output_base_data_path, index=False)

    # Write summary data to file as CSV
    output_summary_data_path = os.path.join(output_dir, OUTPUT_FILENAME)
    output, output_extended = enroll_summarize_dataframe(output)
    output.to_csv(output_summary_data_path, index=False)

    # Write extended data to file as CSV
    output_extended_data_path = os.path.join(output_dir, OUTPUT_FILENAME_EXTENDED)
    output_extended.to_csv(output_extended_data_path, index=False)

    # Clean up
    shutil.rmtree(ZIP_NAME.strip('.zip') + '/')


if __name__ == '__main__':
    print('Beginning data conversion...')
    print('')
    main()
    print('')
    print('Finished.')
