# Development Roadmap

A place to track development objectives.

### Done

* NCES Pipeline
* NAEP Pipeline
* Census Bureau (Financial) Pipeline
* Sanity Check Script
* Input/Output Staging Directories
* Refactored NCES to Use ["Table Generator"](https://nces.ed.gov/ccd/elsi/tableGenerator.aspx) 
instead of raw spreadsheets
* Capture school district data from NCES
* Added sanity checks for all data files

### To-Do

* Add comprehensive validation testing
* Capture demographics (race/gender) for NAEP data
* Capture financial data from NCES, moving away from the Census Bureau
* Capture faculty data from NCES
* Capture dropout/completion data from NCES
* Capture school district data from NAEP
* Standardize pipelines (maybe use a solid design pattern?)
* Incorporate the NCES-provided tip sheets for using their data
* Add enrichments to the final data (account for inflation, add [regions](https://ies.ed.gov/ncee/edlabs/about/), etc.)
* Simplify the process of adding data for subsequent years
    * (Since there aren't any decent API's, maybe build a Selenium web scraper?)
