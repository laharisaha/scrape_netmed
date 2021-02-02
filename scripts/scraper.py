# import packages
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import time
import datetime

# define the starting point
base = "https://www.netmeds.com/medicine/manufacturers"

# fetch html
resp = get(base)
if resp.status_code != 200:
    raise ConnectionError("Can not connect to url provided")
html = bs(resp.text, "lxml")

# Since all manufacturer names are included in different ul elements, we
# capture them all and then iterate over them one by one

ul_lst = html.find_all("ul", {"class": "alpha-drug-list"})

pharma_dict = {}
for ul_elem in ul_lst:
    for li in ul_elem.find_all("li"):
        txt, href = li.find("a").text, li.find("a")['href']
        pharma_dict[txt[:txt.rfind("(")].strip()] = href
med_list = []
total = len(pharma_dict)
idx = 0
start = time.time()
for pharma, url in pharma_dict.items():
    idx += 1
    resp = get(url)
    if resp.status_code != 200:
        continue
    html = bs(resp.text, "lxml")
    med_list.extend([(pharma, li.find("a").text, li.find("a")["href"])
                     for li in html.find_all("li", {"class": "product-item"})])
    curr = time.time()
    avg = (curr - start) / idx
    etf = (total - idx) * avg
    avg = "{:.2f} sec/page".format(avg) if avg > 1 else "{:.2f} pages/sec".format(1 / avg)
    print("Scraping details | avg speed: {}| ETF: {}".format(avg, datetime.timedelta(seconds=int(etf))), end="\r")

med_df = pd.DataFrame(med_list, columns=["Manufacturer", "Medicine Name", "Detail Link"])

med_df.to_excel("data/output.xlsx", index=False)

