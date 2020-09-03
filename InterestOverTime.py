from pytrends.request import TrendReq
import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import json
import time
import os

output_folder = "./output_csv%s/" % datetime.datetime.now().strftime("%Y-%m-%d")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

pd.options.mode.chained_assignment = None  # default='warn'
timezone_offset = -330 # INDIA
# timezone_offset = -480 # Phillipines

pytrends = TrendReq(hl='en-US', timeout=(10, 25), tz=timezone_offset, retries=10, backoff_factor=0.5)

date_entry = input('Enter a start date in YYYY-MM-DD format: ')
year, month, day = map(int, date_entry.split('-'))
date1 = datetime.date(year, month, day)

date_entry = input('Enter a end date in YYYY-MM-DD format: ')
year, month, day = map(int, date_entry.split('-'))
date2 = datetime.date(year, month, day)

t_frame = date1.strftime("%Y-%m-%d") + " " + date2.strftime("%Y-%m-%d")

cat_df = pd.read_csv("categories_defined.csv")
cat_names = cat_df["name"].tolist()
cat_ids = cat_df["id"].tolist()

interest_df = pd.DataFrame()
interest_monthly_df = pd.DataFrame()

## Category Level Call
for i in range(len(cat_ids)):
    # print(i, cat_ids[i], cat_names[i])
    if(i%20==0):
        time.sleep(60)
    try:
        pytrends.build_payload([""], cat=cat_ids[i], timeframe=t_frame, geo='PH', gprop='')
    except:
        time.sleep(60)
        pytrends.build_payload([""], cat=cat_ids[i], timeframe=t_frame, geo='PH', gprop='')
    data = pytrends.interest_over_time()
    if(data.empty):
        print(cat_names[i], "has no results")
        continue
    data = pd.DataFrame(data.to_records())
    data1 = data[["date",""]]
    data1.columns = ['date', 'hits']
    data1['date'] = data1['date'].dt.date
    data1["keyword"] = cat_names[i]
    data1["geo"] = "PH"
    data1["time"] = t_frame
    data1["gprop"] = "web"
    data1["category"] = cat_ids[i]
    interest_df = interest_df.append(data1)
    
    # Group data in monthly
    # print(data)
    g = data[["date",""]].set_index("date").groupby(pd.Grouper(freq="M"))
    g = pd.DataFrame(g.sum().to_records())
    g["date"] = g["date"] - pd.tseries.offsets.MonthBegin(1)
    g.columns = ["date", "hits"]
    g['date'] = g['date'].dt.date
    g["keyword"] = cat_names[i]
    g["geo"] = "PH"
    g["time"] = t_frame
    g["gprop"] = "web"
    g["category"] = cat_ids[i]
    
    interest_monthly_df = interest_monthly_df.append(g)

interest_df.reset_index().to_csv(output_folder+"interest_over_time_%s.csv" % t_frame)
interest_monthly_df.reset_index().to_csv(output_folder+"interest_monthly_df_%s.csv" % t_frame)