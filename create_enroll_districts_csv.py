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

# The name of the input CSV
INPUT_FILENAME = 'enroll_districts_raw.csv'

# The name of the output CSVs
OUTPUT_FILENAME = 'enroll_districts.csv'

# State names
STATES = us.STATES

# Useful regular expressions
doublespace = re.compile(r'  ')
numbersonly = re.compile(r'\d+')
surveyyear = re.compile(r'\d\d\d\d')


def find_specs(col_name):
    """
    Parses a column name for attributes and returns them.

    :param col_name:
    :return:[YEAR, GRADE, RACE, GENDER]
    """
    # Input in the form of YEAR_GRADE_RACE_GENDER
    spec_list = col_name.split('_')
    return spec_list


def restructure_enroll_data(input_df):
    """
    Restructure enrollment data from NCES by putting
    rows in YEAR_STATE format.

    :return:
    """
    data_cols = input_df.columns.to_list()
    ## Ignore the first two columns, "Agency Name" and "State Name"
    data_cols = data_cols[2:]

    year_range = [find_specs(x)[0] for x in data_cols]
    ## Remove duplicate years
    year_range = sorted(list(set(year_range)))

    # Drop districts w/ no associated State Name
    input_df = input_df[input_df['State Name'].notna()]

    # Combine districts and states into a single column
    input_df['district_key_series'] = input_df['Agency Name'] + '_' + input_df['State Name']
    district_list = sorted(list(set(input_df['district_key_series'].to_list())))

    # For each district and year, create a primary key
    output_df = pd.DataFrame()
    primary_key = []
    for district in district_list:
        for year in year_range:
            primary_key.append('{0}_{1}'.format(year, str(district).upper()))

    output_df['PRIMARY_KEY'] = primary_key
    output_df['DISTRICT'] = [x.split('_')[1] for x in output_df['PRIMARY_KEY']]
    output_df['YEAR'] = [x.split('_')[0] for x in output_df['PRIMARY_KEY']]

    # Convert each <YEAR_GRADE_RACE_GENDER> column,
    # producing <GRADE_RACE_GENDER> columns
    for col_name in data_cols:
        ## Generate the new column
        year = find_specs(col_name)[0]
        new_col_name = col_name.replace('{0}_'.format(year), '')
        output_df[new_col_name] = pd.Series()

    # Populate the output dataframe using the input dataframe
    ## There has to be a nicer way to do this...
    for col_name in data_cols:
        # Parse the column name
        specs = find_specs(col_name)
        year = specs[0]
        grade = specs[1]
        race = specs[2]
        gender = specs[3]

        # Import rows from the input data into the output dataframe
        column_data = input_df[['district_key_series', col_name]]
        target_col = '{0}_{1}_{2}'.format(grade, race, gender)
        target_col_data = output_df[['DISTRICT', 'YEAR', target_col]]
        target_col_data = target_col_data[(target_col_data['YEAR'].str.contains(year))]

        ## Avoid dealing with index issues by converting to list
        target_col_data[target_col] = column_data[col_name].to_list()

        # Set the column type to numeric, filtering out strings
        target_col_data[target_col] = pd.to_numeric(target_col_data[target_col], errors='coerce')

        output_df[target_col].update(target_col_data[target_col])

    return output_df


def main(logger=None, input_dir=None, output_dir=None, sanity_dir=None):
    # Notify user
    logger.debug('Parsing ' + str(INPUT_FILENAME) + '...')

    # Unpack the data
    input_data = pd.read_csv(os.path.join(input_dir, INPUT_FILENAME))

    # Transform the data (YEAR_DISTRICT_STATE format)
    output_df = restructure_enroll_data(input_data)

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
