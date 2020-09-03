from pytrends.request import TrendReq
import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import json
import time
from pandas.io.json._normalize import nested_to_record
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

total_t_frame = date1.strftime("%Y-%m-%d") + " " + date2.strftime("%Y-%m-%d")

enddates = pd.date_range(date1, date2 , freq='1M').tolist()
startdates = pd.to_datetime([x.date() - pd.tseries.offsets.MonthBegin(1) for x in enddates]).tolist()

t_frames = []
for i in range(len(startdates)):
    s = startdates[i].date().strftime("%Y-%m-%d")
    e = enddates[i].date().strftime("%Y-%m-%d")
    t_frames.append(s + " " + e)
    
cat_df = pd.read_csv("categories_defined.csv")
cat_names = cat_df["name"].tolist()
cat_ids = cat_df["id"].tolist()

def get_related_topics(catno, timeframe):
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
    request_json = pytrends.related_topics_widget_list[0]
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
        temp = req_json["default"]["rankedList"][0]["rankedKeyword"]
        top_df = pd.DataFrame([nested_to_record(d, sep='_') for d in temp])[["topic_title", "topic_type", "formattedValue"]]
    except KeyError:
        # in case no top queries are found, the lines above will throw a KeyError
        top_df = pd.DataFrame(columns=["topic_title", "topic_type", "formattedValue"])

    # rising queries
    try:
        temp = req_json["default"]["rankedList"][1]["rankedKeyword"]
        rising_df = pd.DataFrame([nested_to_record(d, sep='_') for d in temp])[["topic_title", "topic_type", "formattedValue"]]
    except KeyError:
        # in case no rising queries are found, the lines above will throw a KeyError
        rising_df = pd.DataFrame(columns=["topic_title", "topic_type", "formattedValue"])

    return(top_df,rising_df)

related_topics_monthly = pd.DataFrame()

ctr = 0
for i in range(len(cat_ids)):
    print(i, cat_ids[i], cat_names[i])
    rt_top_df, rt_rising_df = get_related_topics(cat_ids[i], total_t_frame)
    
    if(len(rt_top_df)==0 and len(rt_top_df)==0):
        print("skipping ", cat_names[i], cat_ids[i])
        continue
        
    for j in range(len(t_frames)):
        ctr += 1
        if(ctr%20==0):
            time.sleep(60)

        rt_top_df, rt_rising_df = get_related_topics(cat_ids[i], timeframe=t_frames[j])
        
        if(len(rt_top_df)==0):
            print(cat_names[i], "has no top topics in", t_frames[j])
        if(len(rt_rising_df)==0):
            print(cat_names[i], "has no rising topics in", t_frames[j])

        rt_top_df.columns = ["topic_title", "topic_type", "subject"]
        rt_rising_df.columns = ["topic_title", "topic_type", "subject"]

        rt_top_df["related_topics"] = "top"
        rt_rising_df["related_topics"] = "rising"
        rt_df = rt_rising_df.append(rt_top_df)

        rt_df = rt_top_df.append(rt_rising_df)

        rt_df["geo"] = "PH"
        rt_df["keyword"] = cat_names[i]
        rt_df["category"] = cat_ids[i]
        rt_df["timeframe"] = datetime.datetime.strptime(t_frames[j].split()[0], "%Y-%m-%d").strftime("%b-%Y")
        related_topics_monthly = related_topics_monthly.append(rt_df)
        
related_topics_monthly.reset_index().to_csv(output_folder+"related_topics_monthly_%s.csv" % total_t_frame)