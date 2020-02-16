"""
A script that generates a sanity check for the data, logging the null values
in the aggregated output and exploring where those nulls stem from.
"""

import os
import pandas as pd
import pprint


def main(logger=None, input_dir=None, output_dir=None, input_filename=None, count_year_nulls=False, year_label='YEAR'):
    logger.debug('Creating data sanity check file...')

    # Load in data
    input_path = os.path.join(input_dir, input_filename)
    input_df = pd.read_csv(input_path)
    sanity_check_output = []

    # High Level Overview
    sanity_check_output.append('Data Description:')
    sanity_check_output.append('\n')
    sanity_check_output.append(input_df.describe().to_csv())
    sanity_check_output.append('\n')

    sanity_check_output.append('Null Counts')
    sanity_check_output.append('\n')
    for col in input_df.columns:
        nulls = input_df[col].isnull().sum()
        sanity_check_output.append(col + ': ' + str(nulls))
        sanity_check_output.append('\n')
    sanity_check_output.append('\n')

    # Nulls by years
    if count_year_nulls:
        null_count_dict = {}
        for year in input_df[year_label].unique():
            null_count_dict[year] = {}
            yr_df = input_df[input_df[year_label] == year]
            for col in input_df.columns:
                nulls = yr_df[col].isnull().sum()
                null_count_dict[year][col] = nulls
        sanity_check_output.append(pprint.pformat(null_count_dict))
        sanity_check_output.append('\n')

    output_filename = f'sanity_check_{input_filename}'
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w+') as f:
        f.writelines(sanity_check_output)


if __name__ == '__main__':
    print('Beginning data sanity check...')
    print('')
    main()
    print('')
    print('Finished.')
