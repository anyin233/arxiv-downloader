from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.auto import trange
import requests
import os

from config import *


def parse_page_number(soup):
  strings = soup.find_all("div", class_="paging")[0].strings
  page_string = list(strings)[0]
  num_papers = int(''.join(filter(str.isdigit, page_string)))
  return num_papers

def get_arxiv_ids(soup):
  id_nodes = soup.find_all("a", title="Abstract")
  ids = [node["id"] for node in id_nodes]
  title_nodes = soup.find_all("div", class_="list-title mathjax")
  titles = [list(node.strings)[1].strip() for node in title_nodes]
  id_dict = {}
  for id, title in zip(ids, titles):
    id_dict[id] = title
  return id_dict

pbar_year = trange(int(START_YEAR), int(END_YEAR)+1)

for year in pbar_year:
    pbar_year.set_description(f"Processing {year}")
    url = f"{BASE_URL}/list/{FIELD}/{year}"
    pbar_outer = trange(1, 13)
    
    for m in pbar_outer:
        murl = f"{url}-{m:02d}"
        pbar_outer.set_description(f"Processing {year}-{m:02d}")
        # soup = BeautifulSoup(open(f"{url}.html"), "lxml")
        response = requests.get(murl)
        soup = BeautifulSoup(response.content, "lxml-xml")
        # Get the number of papers
        num_papers = parse_page_number(soup)
        # print(f"Number of papers: {num_papers}")
        paper_of_this_month = []
        pbar_inner = trange(0, num_papers, 2000)
        for skip_id in pbar_inner:
          skurl = f"{murl}?skip={skip_id}&show=2000"
          response = requests.get(skurl)
          soup = BeautifulSoup(response.content, "lxml-xml")
          ids = get_arxiv_ids(soup)
          paper_of_this_month.extend(ids.items())
          if len(ids) == 0:
            print("No more papers")
        # String into csv file
        with open(os.path.join(LIST_PATH, f"{year}-{m:02d}.csv"), "w") as f:
          f.write("paper_id,title\n")
          for paper_id, title in paper_of_this_month:
            f.write(f"{paper_id},\"{title}\"\n")