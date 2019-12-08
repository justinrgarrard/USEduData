"""
A script that generates a sanity check for the data, logging the null values
in the aggregated output and exploring where those nulls stem from.
"""

import os
import pandas as pd
import pprint

INPUT_FILENAME = 'enroll_states.csv'
OUTPUT_FILENAME = 'enroll_sanity_check.txt'


def main(logger=None, input_dir=None, output_dir=None):
    logger.debug('Creating enrollment data sanity check file...')

    # Load in data
    input_path = os.path.join(input_dir, INPUT_FILENAME)
    all_df = pd.read_csv(input_path)
    sanity_check_output = []

    # High Level Overview
    sanity_check_output.append('Data Description:')
    sanity_check_output.append('\n')
    sanity_check_output.append(all_df.describe().to_csv())
    sanity_check_output.append('\n')

    sanity_check_output.append('Null Counts')
    sanity_check_output.append('\n')
    for col in all_df.columns:
        nulls = all_df[col].isnull().sum()
        sanity_check_output.append(col + ': ' + str(nulls))
        sanity_check_output.append('\n')
    sanity_check_output.append('\n')

    # Nulls by years
    null_count_dict = {}
    for year in all_df['YEAR'].unique():
        null_count_dict[year] = {}
        yr_df = all_df[all_df['YEAR'] == year]
        for col in all_df.columns:
            nulls = yr_df[col].isnull().sum()
            null_count_dict[year][col] = nulls
    sanity_check_output.append(pprint.pformat(null_count_dict))
    sanity_check_output.append('\n')

    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    with open(output_path, 'w+') as f:
        f.writelines(sanity_check_output)


if __name__ == '__main__':
    print('Beginning data sanity check...')
    print('')
    main()
    print('')
    print('Finished.')
