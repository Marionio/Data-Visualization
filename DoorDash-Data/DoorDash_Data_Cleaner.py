# Import neccesary libraries
import pandas as pd

data=pd.read_csv("dasher_delivery_information.csv")

# cleaning strings
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"\(.*\)","", regex=True).str.strip()
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"7-Eleven","7 Eleven")
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Me-.*","Me N Ed's", regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Jack.*","Jack in the Box",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Chick.*","Chick Fil A", regex=True)
# Before the '-'
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"-.*","", regex=True).str.strip()
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"#.*","", regex=True).str.strip()

# Fixing restaurants names
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Porterville","Vallarta", regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Applebee's.*","Applebee's", regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Subway.*","Subway", regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Baskin","Baskin Robbins")
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Script.*","Rite Aid",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Little.*","Little Caesar's",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Wingstop.*","Wingstop",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Panera.*","Panera",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.replace(r"Von.*","Von's",regex=True)
data['STORE_NAME']= data['STORE_NAME'].str.strip()

# Filtering out unwanted values
data.drop(data.index[data['STORE_NAME'] == '[DNU][[COO]]'], inplace=True)
data.drop(data.index[data['STORE_NAME'] == 'Delete COO'], inplace=True)

# Cleaning the columns for times
data['ORDER_CREATED_TIME'] =data['ORDER_CREATED_TIME'].str.replace(r"\..*","", regex=True)
data['ACTUAL_PICKUP_TIME'] =data['ACTUAL_PICKUP_TIME'].str.replace(r"\..*","", regex=True)
data['ACTUAL_DELIVERY_TIME'] =data['ACTUAL_DELIVERY_TIME'].str.replace(r"\..*","", regex=True)

# Changing values to datetime
data['ORDER_CREATED_TIME'] =pd.to_datetime(
    data['ORDER_CREATED_TIME'], format = '%Y/%m/%d %H:%M:%S')

data['ACTUAL_PICKUP_TIME'] =pd.to_datetime(
    data['ACTUAL_PICKUP_TIME'], format = '%Y/%m/%d %H:%M:%S')

data['ACTUAL_DELIVERY_TIME'] =pd.to_datetime(
    data['ACTUAL_DELIVERY_TIME'], format = '%Y/%m/%d %H:%M:%S')

# Fixing the time
from pytz import timezone

data["ORDER_CREATED_TIME"] = data["ORDER_CREATED_TIME"].dt.tz_localize('GMT').dt.tz_convert('US/Pacific').dt.tz_localize(None)
data["ACTUAL_PICKUP_TIME"] = data["ACTUAL_PICKUP_TIME"].dt.tz_localize('GMT').dt.tz_convert('US/Pacific').dt.tz_localize(None)
data["ACTUAL_DELIVERY_TIME"] = data["ACTUAL_DELIVERY_TIME"].dt.tz_localize('GMT').dt.tz_convert('US/Pacific').dt.tz_localize(None)

# Adding new columns, re-aranging the columns
TIME_TO_PICKUP = data['ACTUAL_PICKUP_TIME'] - data['ORDER_CREATED_TIME']
TIME_TO_DELIVER = data['ACTUAL_DELIVERY_TIME'] - data['ACTUAL_PICKUP_TIME']
TOTAL_TIME = TIME_TO_PICKUP + TIME_TO_DELIVER
data['TIME_TO_PICKUP'] = TIME_TO_PICKUP
data['TIME_TO_DELIVER'] = TIME_TO_DELIVER
data['TOTAL_TIME'] = TOTAL_TIME
new_cols = ['STORE_NAME','TOTAL_TIME', 'TIME_TO_PICKUP', 'TIME_TO_DELIVER', 'SUBTOTAL_IN_CENTS', 'TOTAL_ITEM_COUNT', 'ORDER_CREATED_TIME', 'ACTUAL_PICKUP_TIME', 'ACTUAL_DELIVERY_TIME', 'ORDER_STATUS']
data =data[new_cols]

# Changing cents to dollars
data["SUBTOTAL_IN_CENTS"] = (data["SUBTOTAL_IN_CENTS"] /100)
data.drop(data.index[data['SUBTOTAL_IN_CENTS'] == 0], inplace=True)
data.rename(columns = {"SUBTOTAL_IN_CENTS":"SUBTOTAL_IN_DOLLARS"}, inplace=True)

# Saving to csv
data.to_csv("CMaster.csv", index=False)

