# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from src import create_finance_states_csv, create_enroll_states_summary_csv, create_enroll_districts_csv, \
    create_finance_districts_csv, create_states_all_csv, create_naep_states_raw_csv, create_naep_states_csv, \
    create_naep_states_summary_csv, create_enroll_districts_raw_csv, create_enroll_states_csv, \
    create_enroll_states_raw_csv


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.argument('interim_filepath', type=click.Path())
def main(input_filepath, output_filepath, interim_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('making final data set from raw data')

    # Set shared input/output directories
    INPUT_DIR = input_filepath
    OUTPUT_DIR = output_filepath
    SANITY_DIR = interim_filepath

    LOGGER.info('Starting data processing...')

    # Create district and state summary files
    ## District
    create_finance_districts_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    ## State
    create_finance_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

    # Create a summary file from the NAEP data
    ## District

    ## State
    create_naep_states_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    create_naep_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    create_naep_states_summary_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

    # Create a summary file from the NCES data
    ## District
    create_enroll_districts_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    create_enroll_districts_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

    ## State
    create_enroll_states_raw_csv.main(LOGGER, INPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    create_enroll_states_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)
    create_enroll_states_summary_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

    # Create a summary file from all the data
    ## District

    ## State
    create_states_all_csv.main(LOGGER, OUTPUT_DIR, OUTPUT_DIR, SANITY_DIR)

    LOGGER.info('Data processing complete!')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s: %(filename)s [%(funcName)s]- %(message)s', level=logging.DEBUG)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
