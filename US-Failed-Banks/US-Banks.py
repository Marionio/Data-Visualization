import pandas as pd

bank_data = pd.read_csv("banklist.csv", encoding= 'ISO-8859-1') # https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/index.html FDIC failed banking institutions (03/13/23)

print(bank_data.info())
