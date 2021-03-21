'''
this python-file demonstrates the basic usage of the pyAvaCore module
'''

from avacore import pyAvaCore

print ('Enter region ID to print report:')
region_id = input("(e.g. 'FR-01' or 'AT-07-05' ): ")
if region_id == '':
    region_id = 'AT-07-01'
print('Download Report for:', region_id)

reports, provider, url = pyAvaCore.get_reports(region_id)
for report in reports:
    report.cli_out()
