'''
this python-file demonstrates the basic usage of the pyAvaCore module
'''

from avacore import pyAvaCore

print ('Enter region ID to print report:')
region_id = input("(e.g. 'FR-01' or 'AT-07-05'): ")

# Suported region ID's are listed in the REGIONS.md file
if region_id == '':
    region_id = 'AT-07-01'

print('Download Report for:', region_id)
reports, provider, url = pyAvaCore.get_reports(region_id)

# reports contains all reports, that are delivered in a common provided file. Often this is all the reports of one state.
# If you want to have a report only for the region entered, you need to filter the reports list by the 'valid region' parameter.
# The report structure is defined in the AvaReport class in pyAvaCore.py

for report in reports:
    report.cli_out()
