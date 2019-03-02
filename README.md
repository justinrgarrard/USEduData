# US Educational Data Processor

A compilation of several education databases, summarized into a single file (states_all.csv).

The source data is too large to host on GitHub, but it can be pulled from the corresponding Kaggle 
[link](https://www.kaggle.com/noriuk/us-education-datasets-unification-project/home).

### Usage

1. Download the source data from Kaggle (all the .zip files).
2. Install the relevant Python packages if necessary (see requirements.txt).
3. Run main.py to generate output data (all the .csv files).

### Overview

The data is broken down into three main categories:

* **Demographics**: 
A breakdown of students enrolled in schools by school year.

* **Financial Status**: 
A breakdown of states by revenue and expenditure.

* **Academic Achievement**: 
A breakdown of student performance as assessed by the corresponding exams (math and reading, 
grades 4 and 8).

### Data: Demographics

Drawn from the NCES (National Center for Educational Statistics).

```bash
PRIMARY_KEY,STATE,YEAR,GRADES_PK,GRADES_KG,GRADES_4,GRADES_8,GRADES_12,GRADES_1_8,GRADES_9_12,GRADES_KG_12,GRADES_ALL
```

* GRADES_PK: Number of students in Pre-Kindergarten education.

* GRADES_4: Number of students in fourth grade.

* GRADES_8: Number of students in eighth grade.

* GRADES_12: Number of students in twelfth grade.

* GRADES_1_8: Number of students in the first through eighth grades.

* GRADES 9_12: Number of students in the ninth through twelfth grades.

* GRADES_KG_12: Number of students in Kindergarten through twelfth grade.

* GRADES_ALL: The count of all students in the state. Comparable to ENROLL in the financial data (which is the U.S.
Census Bureau's estimate for students in the state).

The extended version of states_all contains additional columns that breakdown enrollment by race and gender. For example:

* Grades_ALL_AS: Number of students whose ethnicity was classified as "Asian".

* Grades_ALL_ASM: Number of male students whose ethnicity was classified as "Asian".

* Grades_ALL_ASF: Number of female students whose ethnicity was classified as "Asian".

The represented races include AM (American Indian or Alaska Native), AS (Asian), HI (Hispanic/Latino), BL (Black or African American), WH (White), HP (Hawaiian Native/Pacific Islander), and TR (Two or More Races). The represented genders include M (Male) and F (Female).


### Data: Financials

Drawn from U.S. Census Bureau records.

```bash
PRIMARY_KEY,STATE,YEAR,ENROLL,TOTAL_REVENUE,FEDERAL_REVENUE,STATE_REVENUE,LOCAL_REVENUE,TOTAL_EXPENDITURE,INSTRUCTION_EXPENDITURE,SUPPORT_SERVICES_EXPENDITURE,OTHER_EXPENDITURE,CAPITAL_OUTLAY_EXPENDITURE
```

* ENROLL: The U.S. Census Bureau's count for students in the state. Should be comparable to GRADES_ALL (which is the
NCES's estimate for students in the state).

* TOTAL REVENUE: The total amount of revenue for the state.
    * FEDERAL_REVENUE
    * STATE_REVENUE
    * LOCAL_REVENUE
    
* TOTAL_EXPENDITURE: The total expenditure for the state.
    * INSTRUCTION_EXPENDITURE
    * SUPPORT_SERVICES_EXPENDITURE
    * CAPITAL_OUTLAY_EXPENDITURE
    * OTHER_EXPENDITURE
    
### Data: Achievement

Drawn from NAEP data (National Assessment of Educational Progress) collected by the NCES.
NAEP data is collected on odd numbered years (even-numbered years contain NA's).

```bash
PRIMARY_KEY,STATE,YEAR,AVG_MATH_4_SCORE,AVG_MATH_8_SCORE,AVG_READING_4_SCORE,AVG_READING_8_SCORE
```

* AVG_MATH_4_SCORE: The state's average score for fourth graders taking the NAEP math exam.

* AVG_MATH_8_SCORE: The state's average score for eight graders taking the NAEP math exam.

* AVG_READING_4_SCORE: The state's average score for fourth graders taking the NAEP reading exam.

* AVG_READING_8_SCORE: The state's average score for eighth graders taking the NAEP reading exam.

### Methodological Notes

* Spreadsheets for NCES enrollment data for 2014, 2011, 2010, and 2009 
were modified to place key data on the same sheet, making scripting easier.

* The column 'ENROLL' represents the U.S. Census Bureau data value (financial data), while the
column 'GRADES_ALL' represents the NCES data value (demographic data). Though the two organizations
correspond on this matter, these values (which are ostensibly the same) do vary. Their documentation chalks this
up to differences in membership (i.e. what is and is not a fourth grade student).

* Enrollment data from NCES has seen a number of changes across survey years. One of the more notable is that data 
on student gender does not appear to have been collected until 2009. The information in states_all_extended.csv 
reflects this.

* NAEP test score data is only available for certain years

* The current version of this data is concerned with state-level patterns. It is the author's hope that future
versions will allow for school district-level granularity.

* The licensing of this data states that it must not be used to identify specific students or schools. So
don't do that.

### Data Pipeline

1. The main function is called.

2. Subroutines for each category are run (demographics, financials, and achievement).

3. Each subroutine extracts annual spreadsheets from a corresponding zip file.

4. Annual reports are transformed into Pandas data objects, cleaned, and collected into a single spreadsheet for that
category.

5. The category spreadsheets are combined into a master spreadsheet (states_all.csv) that includes summary columns
for every category, for every year, and for every state.

6. A data sanity check is run, generating a text file (sanity_check.txt) that reports on null values.

### Version Info

* v0.1: Initial commit.
* v0.2: Added demographic data for enrollment (race/gender).
