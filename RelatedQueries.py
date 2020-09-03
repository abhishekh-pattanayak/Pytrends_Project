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

def get_related_queries(catno, timeframe):
    """
    Gets related queries
    """
    kw_list = [""]
    # Create Pytrend Client
    try:
        pytrends.build_payload([""], cat=cat_ids[i], timeframe=t_frame, geo='PH', gprop='')
    except:
        time.sleep(60)
        pytrends.build_payload([""], cat=cat_ids[i], timeframe=t_frame, geo='PH', gprop='')
    
    # Form Request
    related_payload = dict()
    request_json = pytrends.related_queries_widget_list[0]
    related_payload["req"] = json.dumps(request_json["request"])
    related_payload["token"] = request_json["token"]
    related_payload["tz"] = pytrends.tz
    
    # Send Request
    req_json = pytrends._get_data(
        url=TrendReq.RELATED_QUERIES_URL,
        method=TrendReq.GET_METHOD,
        trim_chars=5,
        params=related_payload,
    )
    
    # return req_json
    # Tabulate Rising & Top searches.
    try:
        top_df = pd.DataFrame(req_json["default"]["rankedList"][0]["rankedKeyword"])
        top_df = top_df[["query", "formattedValue"]]
    except KeyError:
        # in case no top queries are found, the lines above will throw a KeyError
        top_df = pd.DataFrame(columns=["query", "formattedValue"])

    # rising queries
    try:
        rising_df = pd.DataFrame(req_json['default']['rankedList'][1]["rankedKeyword"])
        rising_df = rising_df[['query', 'formattedValue']]
    except KeyError:
        # in case no rising queries are found, the lines above will throw a KeyError
        rising_df = pd.DataFrame(columns=["query", "formattedValue"])

    return(top_df,rising_df)

related_queries = pd.DataFrame()

for i in range(len(cat_ids)):
    # print(i, cat_ids[i], cat_names[i])
    if(i%20==0):
        time.sleep(20)
    rq_top_df, rq_rising_df = get_related_queries(cat_ids[i], t_frame)
    if(len(rq_top_df)==0):
        print(cat_names[i], "has no top queries")
    if(len(rq_rising_df)==0):
        print(cat_names[i], "has no rising queries")
    
    rq_top_df.columns = ["value", "subject"]
    rq_rising_df.columns = ["value", "subject"]
    
    rq_top_df["related_queries"] = "top"
    rq_rising_df["related_queries"] = "rising"
    
    rq_df = rq_top_df.append(rq_rising_df)
    
    rq_df["geo"] = "PH"
    rq_df["keyword"] = cat_names[i]
    rq_df["category"] = cat_ids[i]
    related_queries = related_queries.append(rq_df)
    
related_queries.reset_index().to_csv(output_folder+"related_queries_%s.csv" % t_frame)