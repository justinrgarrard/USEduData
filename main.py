"""
A driver function to build the full set of data files.
"""

import create_finance_districts_csv
import create_finance_states_csv
import create_naep_states_csv
import create_enroll_states_csv
import create_states_all_csv
import data_sanity_check

# Create district summary file
create_finance_districts_csv.main()

# Create state summary file from district summary
create_finance_states_csv.main()

# Create a summary file from the NAEP data
create_naep_states_csv.main()

# Create a summary file from the NCES data
create_enroll_states_csv.main()

# Create a denormalized file from all the data
create_states_all_csv.main()

# Create a sanity check file from the aggregated data
data_sanity_check.main()
