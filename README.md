# Pytrends_Project
Scripts and Automation Project - Google Trends Monthly and Ad Hoc Data Scraping

## Google Trend Extraction

#### Languages, Libraries and API's used:- 
Python, pytrends, Google Trends API

The goal of this freelancing project was creating an automation for generating monthly reports for 56 categories concentrating on 3 kinds of data: interest over time, related queries(rising & top) and related topics(rising & top). pytrends library doesn't support empty keyword for related queries and related topics although Google Trends API does. So some functions of the pytrends library needed to be overridden to extract the required data. The scripts were scheduled to run monthly and generate reports along with ad hoc scripts for testing or running ad hoc queries.

##### Benefits: 
- The production code was scheduled as cron jobs and also in Windows Task Scheduler. So the data extraction work load for the developers in the client's production team was reduced.
- Google Trends API is not available explicitly. For Python, pytrends is the most popular library and using the overridden code the client was able to continue using pytrends, a library he was acquainted with.
- The script was tested for blocking issues. According to the docs and testing results, limitations to the API call frequency and speed were set in the production script.
