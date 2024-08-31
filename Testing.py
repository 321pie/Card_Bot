from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import requests

SPREADSHEET_ID = "1zUblRLIugMxcqi-2R0AiEAx7gt9FnujT5ik7JB0viaw"

guid1 = 0 #for the 1st sheet
guid2 = 2086363072 #for the 2nd sheet
act = requests.get(f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=%s' % guid2)

dataact = act.content.decode('utf-8') #To convert to string for Stringio
actdf = pd.read_csv(StringIO(dataact), index_col=[0], parse_dates=[0], thousands=',')

print(actdf.loc[0])
actdf.loc[0, "Username"] = "LSRoserade"
print(actdf.loc[0])

# #act.content = actdf.to_csv().encode('utf-8')

#print(requests.put(f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/import?format=csv&gid=%s' % guid2, actdf.to_csv().encode('utf-8')))