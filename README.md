# US Educational Data Processor

A compilation of several education databases, summarized into a single file (states_all.csv).

**NOTE**: Project is in development.

**NOTE**: Data is too large for a GitHub repo. Working on a hosting solution.

### Overview

The data is broken down into three main categories:

* **Demographics**: 
A breakdown of students enrolled in schools by age, race, and gender.

* **Financial Status**: 
A breakdown of school districts by revenue and expenditure.

* **Academic Achievement**: 
A breakdown of student performance as assessed by the corresponding exams.

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

* GRADES_KG_12: Number of students in kindergarten through twelfth grade.

* GRADES_ALL: The count of all students in the state. Comparable to ENROLL in the financial data (which is the U.S.
Census Bureau's estimate for students in the state).

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
    
* TOTAL_EXPENDITURE:
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
correspond on this matter, these values (which are ostensibly the same) do vary. Documentation chalks this
up to differences in membership (i.e. what is and is not a fourth grade student).

* The current version of this data is concerned with state-level patterns. It is the author's hope that future
versions will allow for school district-level granularity.

* The licensing of this data states that it must not be used to identify specific students or schools. So
don't do that.
