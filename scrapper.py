import requests
from bs4 import BeautifulSoup
import csv

from requests_cache import ALL_METHODS

SPECIAL_CHAR = ['\n', '\t']
CHAR_TO_REMOVE = ['\"', '/>']
COLUMNS_FILE = 'columns.txt'
MUSEUM_ID_FILE = 'museum_id.txt'
#MUSEUM_URL = 'http://www.muis.ee/rdf/objects-by-museum/83529'
MUSEUM_BASE_URL = 'http://www.muis.ee/rdf/objects-by-museum/'
OBJECT_URL = 'http://opendata.muis.ee/object/1858783'
PERSON_GROUP_BASE_URL = 'http://opendata.muis.ee/person-group/'
CSV_RESULTS_FILE = 'EstonianMuseumCollections.csv'

# remove specified characters (specified in a list) from the given string
def remove_character(char_list, str):
    for char in char_list:
        str = str.replace(char, '')
    return str

# get all lines from a file and return a list in which each element is a line
def get_columns(file):
    file = open(file, 'r')
    lines = file.readlines()
    columns = []
    for line in lines:
        columns.append(remove_character(SPECIAL_CHAR, line))
    return columns

def update_object_dict(object_dict, keys_list, values_list):
    for key in object_dict:
        if key in keys_list:
            object_dict[key] = values_list[keys_list.index(key)]
    return object_dict

def get_items_text(items_list):
    items_text = []
    for item in items_list:
        try:
            items_text.append(item.get_text())
        except:
            continue
    return items_text

def get_object_data_dict(table_list, default_keys):
    object_dict = dict.fromkeys(default_keys) # init object dict
    for table in table_list:
        # all_tr = table.find_all("tr")
        all_th = table.find_all("th")
        all_td = table.find_all("td")
        all_th_text = get_items_text(all_th)
        all_td_text = get_items_text(all_td)
        object_dict = update_object_dict(object_dict, all_th_text, all_td_text)
    return object_dict

def get_objects_url(museums_url):
    return

def scrap_objects(object_url_list, object_infos):
    objects_info_list = []
    for object_url in object_url_list:
        object_page = requests.get(object_url)
        object_soup = BeautifulSoup(object_page.content, "html.parser")
        table_div = object_soup.find('div' , {'id': 'general_museaal'})
        table_data = table_div.find_all('table', attrs={'class': 'data'}) # table_data should be a list with 2 elements : <table class="data highlighted"> and <table class="data">
        object_dict = get_object_data_dict(table_data, object_infos)
        object_value_list = list(object_dict.values())
        # add steps here for all others values
        objects_info_list.append(object_value_list)
    return objects_info_list

object_url_list = [OBJECT_URL]
columns = get_columns(COLUMNS_FILE)
infos = scrap_objects(object_url_list, columns)
print(infos)


