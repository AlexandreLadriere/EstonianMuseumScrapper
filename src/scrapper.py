import csv
import re
import os

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

SPECIAL_CHAR = ['\n', '\t']
TECHNIC_SUB_DATA = ['Tehnika', 'Värvus', 'Mõõdud']
RESOURCES_FOLDER = 'resources/'
COLUMNS_FILE = 'columns.txt'
MUSEUM_ID_FILE = 'museum_id.txt'
MUSEUM_BASE_URL = 'http://www.muis.ee/rdf/objects-by-museum/'
PERSON_GROUP_BASE_URL = 'http://opendata.muis.ee/person-group/'
CSV_RESULTS_FILE = 'EstonianMuseumCollections.csv'
SRC_LANG = 'et'
DEST_LANG = 'fr'
TRANSLATE = True

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

def get_objects_url(museum_url):
    pattern = 'resource="(.*)"/>'
    museum_page = requests.get(museum_url)
    object_url_list = re.findall(pattern, museum_page.text)
    return object_url_list

def translate(text, src, dest):
    translator = Translator()
    translation = translator.translate(text, src=src, dest=dest)
    return translation.text

def translate_list(input_list, lg_src, lg_dest):
    translated_list = []
    for info in input_list:
        try:
                translated_list.append(translate(info, src=lg_src, dest=lg_dest))
        except:
            translated_list.append(info)
            continue
    return translated_list

def translate_object_info(object_info, lg_src, lg_dest):
    translated_list = object_info
    for i in range(7, len(object_info)):
        try:
                translated_list[i] = translate(object_info[i], src=lg_src, dest=lg_dest)
        except:
            continue
    return translated_list

def scrap_objects(object_url_list, object_infos_name, museum_url):
    objects_info_list = []
    for object_url in object_url_list:
        object_page = requests.get(object_url)
        object_soup = BeautifulSoup(object_page.content, "html.parser")
        # object general data
        table_div = object_soup.find('div' , {'id': 'general_museaal'})
        table_data = table_div.find_all('table', attrs={'class': 'data'}) # table_data should be a list with 2 elements : <table class="data highlighted"> and <table class="data">
        object_dict = get_object_data_dict(table_data, object_infos_name)
        object_dict['ObjectURL'] = object_url
        object_dict['MuseumURL'] = museum_url
        # object image url
        object_image_div = object_soup.find('div' , {'id': 'selected_image'})
        if object_image_div is not None:
            object_image_url = object_image_div.a['href']
        else:
            object_image_url = ''
        object_dict['ImageURL'] = object_image_url
        # format technical info for better translation
        object_dict['Eraldatavad osad'] = format_technic_info(object_dict['Eraldatavad osad'])
        # transform object dict to list and add it to museum object list
        object_value_list = list(object_dict.values())
        if TRANSLATE:
            object_value_list = translate_object_info(object_value_list, SRC_LANG, DEST_LANG)
        print(object_value_list)
        objects_info_list.append(object_value_list)
    return objects_info_list

def save_to_csv(columns, lines, file):
    with open(file, 'w', newline="") as f:
        writer = csv.writer(f)
        if TRANSLATE:
            columns = translate_list(columns, lg_src=SRC_LANG, lg_dest=DEST_LANG)
        writer.writerow(columns)
        for line in lines:
            writer.writerows(line)

def format_technic_info(str):
    formatted_str = str
    for sub_str in TECHNIC_SUB_DATA:
        try:
            formatted_str = formatted_str.replace(sub_str, '\n' + sub_str)
        except:
            continue
    return formatted_str

if __name__ == '__main__':
    cwd = os.getcwd()
    museum_id_list = get_columns(RESOURCES_FOLDER + MUSEUM_ID_FILE)
    columns = get_columns(RESOURCES_FOLDER + COLUMNS_FILE)
    infos_list = []
    for museum_id in museum_id_list:
        object_url_list = get_objects_url(MUSEUM_BASE_URL + museum_id)
        infos = scrap_objects(object_url_list, columns, MUSEUM_BASE_URL + museum_id)
        infos_list.append(infos)
    save_to_csv(columns, infos_list, RESOURCES_FOLDER + CSV_RESULTS_FILE)
