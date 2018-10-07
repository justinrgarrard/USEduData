# US Educational Data Processor

A codebase that pulls U.S. educational data from various sources and converts
them into a form convenient to programmers.

**NOTE**: Project is in development.

**NOTE**: Data is too large for a GitHub repo. Working on a hosting solution.

### Data Contents

* **Demographics**: Drawn from the NCES (National Center for Educational Statistics).
A breakdown of students enrolled in schools by age, race, and gender.

* **Financial Status**: Drawn from U.S. Census Bureau records.
A breakdown of school districts by revenue and expenditure.

* **Academic Achievement**: Drawn from NAEP data (National
Assessment of Educational Progress) collected by the NCES
and SAT data collected by CollegeBoard. A breakdown of
student performance as assessed by the corresponding exams.

### Methodological Notes

* Spreadsheets for NCES enrollment data for 2014, 2011, 2010, and 2009 
were modified to place key data on the same sheet, making scripting easier.

* The column 'ENROLL' represents the U.S. Census Bureau data value (financial data), while the
column 'GRADES_ALL' represents the NCES data value (demographic data). Though the two organizations
correspond on this matter, these values (which are ostensibly the same) do vary. Documentation chalks this
up to differences in membership qualification.

* The current version of this data is concerned with state-level patterns. It is the author's hope that future
versions will allow for school district-level granularity.

* The licensing of this data states that it must not be used to identify specific students
