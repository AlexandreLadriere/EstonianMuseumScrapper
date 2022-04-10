import csv
import re
import os
import unicodedata

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB
from googletrans import Translator

SPECIAL_CHAR = ['\n', '\t']
TECHNIC_SUB_DATA = ['Tehnika', 'Värvus', 'Mõõdud', 'Materjal', 'Moodud']
RESOURCES_FOLDER = 'resources/'
COLUMNS_FILE = 'columns_et.txt'
MUSEUM_ID_FILE = 'museum_id.txt'
COLLECTION_ID_FILE = 'collection_id.txt'
MUSEUM_BASE_URL = 'http://www.muis.ee/rdf/objects-by-museum/'
PERSON_GROUP_BASE_URL = 'http://opendata.muis.ee/person-group/'
COLLECTION_BASE_URL = 'https://www.muis.ee/rdf/collection/'
CSV_RESULTS_FILE = 'EstonianMuseumCollections.csv'
SRC_LANG = 'et'
DEST_LANG = 'fr'
TRANSLATE = False
REMOVE_ACCENT = True
DATABASE = RESOURCES_FOLDER + 'db.json'
CULTURAL_VALUE_ASSESMENT_ET = 'Hinnang museaali kultuurivaartuse kohta' # must not have accent (replace 'ä' by 'a' for example)
CULTURAL_VALUE_ASSESMENT_EN = 'cultural_value_assesment' # must not have accent (replace 'ä' by 'a' for example)
TECHNICAL_INFO_ET = 'Eraldatavad osad'
TECHNICAL_INFO_EN = 'details'
RDF_URL_COL_NAME = 'RdfURL'
IMAGE_URL_COL_NAME = 'ImageURL'
OBJECT_URL_COL_NAME = 'ObjectURL'

GET_COLLECTION = True # if False, then get entire museum collection based on museum id list

def remove_character(char_list, str):
    """
    Return a string in which specified characters have been removed
    
    Parameters
    ----------
    char_list : str
        List of char to remove from the string, eg: ['\n', '\t']
    str : str
        String in which we want to remove characters
    """
    for char in char_list:
        str = str.replace(char, '')
    return str

# get all lines from a file and return a list in which each element is a line
def get_columns(file):
    """
    Return a list in which each element is a row of the specified file
    
    Parameters
    ----------
    file : str
        Path of the file we want to retrieve rows from
    """
    file = open(file, 'r', encoding='utf-8')
    lines = file.readlines()
    columns = []
    for line in lines:
        if REMOVE_ACCENT:
            columns.append(remove_accent(remove_character(SPECIAL_CHAR, line)))
        else:
            columns.append(remove_character(SPECIAL_CHAR, line))
    return columns

def update_object_dict(object_dict, keys_list, values_list):
    """
    Return a dict updated with the given infos for each specified key
    
    Parameters
    ----------
    object_dict : dict
        Dict representing a museum object
    keys_list : list of str
        List containing keys you want to update in the dict
    values_list : list of str
        List containing values for keys you want to update in the dict
    """
    for key in object_dict:
        if key in keys_list:
            object_dict[key] = values_list[keys_list.index(key)]
    return object_dict

def get_items_text(items_list):
    """
    Return a list of str, eg ['info1', 'info2']
    
    Parameters
    ----------
    items_list : list
        List of specific html balise, eg ['<td>info1<td>', '<td>info2<td>']
    """
    items_text = []
    for item in items_list:
        try:
            if REMOVE_ACCENT:
                items_text.append(remove_accent(item.get_text()))
            else:
                items_text.append(item.get_text())
        except:
            continue
    return items_text

def get_object_data_dict(table_list, default_keys):
    """
    Return a dict updated with the given infos for each specified key
    
    Parameters
    ----------
    object_dict : dict
        Dict representing a museum object
    keys_list : list of str
        List containing keys you want to update in the dict
    values_list : list of str
        List containing values for keys you want to update in the dict
    """
    object_dict = dict.fromkeys(default_keys) # init object dict
    for table in table_list:
        # all_tr = table.find_all("tr")
        all_th = table.find_all("th")
        all_td = table.find_all("td")
        all_th_text = get_items_text(all_th)
        all_td_text = get_items_text(all_td)
        object_dict = update_object_dict(object_dict, all_th_text, all_td_text)
    return object_dict

def get_objects_url(url):
    """
    Return a list of url (str) from a rdf database list
    
    Parameters
    ----------
    url : str
        URL of a database (rdf)
    """
    pattern = 'resource="(.*)"/>'
    page = requests.get(url)
    object_url_list = re.findall(pattern, page.text)
    return object_url_list

def translate(text, src, dest):
    """
    Translate a text from a source language to a destination language
    
    Parameters
    ----------
    text : str
        Text to translate
    src : str
        Code of source language, eg: 'fr'
    values_list : list of str
        Code of destination language, eg: 'de'
    """
    translator = Translator()
    translation = translator.translate(text, src=src, dest=dest)
    return translation.text

def translate_list(input_list, lg_src, lg_dest):
    """
    Translate a list of string from a source language to a destination language
    
    Parameters
    ----------
    input_list : list (str)
        List of str to translate
    lg_src : str
        Code of source language, eg: 'fr'
    lg_dest : list of str
        Code of destination language, eg: 'de'
    """
    translated_list = []
    for info in input_list:
        try:
                translated_list.append(translate(info, src=lg_src, dest=lg_dest))
        except:
            translated_list.append(info)
            continue
    return translated_list

def translate_object_info(object_info, lg_src, lg_dest):
    """
    Translate a list of string from a source language to a destination language, starting from the 7th element of each list
    
    Parameters
    ----------
    object_info : list (str)
        List of str to translate
    lg_src : str
        Code of source language, eg: 'fr'
    lg_dest : list of str
        Code of destination language, eg: 'de'
    """
    translated_list = object_info
    for i in range(7, len(object_info)):
        try:
                translated_list[i] = translate(object_info[i], src=lg_src, dest=lg_dest)
        except:
            continue
    return translated_list

def scrap_objects(object_url_list, object_infos_name, url):
    """
    Scrap specific museum object infos, and return a list of lists (one list for each object)
    It also save each object in a json database (tinydb)
    
    Parameters
    ----------
    object_url_list : list (str)
        List of objects url
    object_infos_name : list (str)
        List of info names to look for
    url : str
        URL of the rdf db
    """
    db = TinyDB(DATABASE)
    objects_info_list = []
    for object_url in object_url_list:
        object_page = requests.get(object_url)
        object_soup = BeautifulSoup(object_page.content, "html.parser")
        # object general data
        table_div = object_soup.find('div' , {'id': 'general_museaal'})
        try:
            table_data = table_div.find_all('table', attrs={'class': 'data'}) # table_data should be a list with 2 elements : <table class="data highlighted"> and <table class="data">
        except: 
            table_data = []
        object_dict = get_object_data_dict(table_data, object_infos_name)
        object_dict[OBJECT_URL_COL_NAME] = object_url
        object_dict[RDF_URL_COL_NAME] = url
        # object image url
        object_image_div = object_soup.find('div' , {'id': 'selected_image'})
        if object_image_div is not None:
            object_image_url = object_image_div.a['href']
        else:
            object_image_url = ''
        object_dict[IMAGE_URL_COL_NAME] = object_image_url
        # format technical info for better translation
        object_dict[TECHNICAL_INFO_ET] = format_technic_info(object_dict[TECHNICAL_INFO_ET])
        # rename dict keys by creating new_dict (better to have names without space in db columns titles)
        object_dict_for_db = {}
        for k,v in object_dict.items():
            if k == TECHNICAL_INFO_ET:
                object_dict_for_db[TECHNICAL_INFO_EN] = v
            elif k == CULTURAL_VALUE_ASSESMENT_ET:
                object_dict_for_db[CULTURAL_VALUE_ASSESMENT_EN] = v
            else:
                object_dict_for_db[k] = v
        db.insert(object_dict_for_db)
        # transform object dict to list and add it to museum object list
        object_value_list = list(object_dict.values())
        if TRANSLATE:
            object_value_list = translate_object_info(object_value_list, SRC_LANG, DEST_LANG)
        print(object_value_list)
        objects_info_list.append(object_value_list)
    return objects_info_list

def save_to_csv(columns, lines, file):
    """
    Save a list (columns name) and a list of lists in a csv
    
    Parameters
    ----------
    columns : list (str)
        List of columns name
    lines : list of lists (str)
        List of lists. Each list represent a row
    file : str
        CSV File path to save
    """
    with open(file, 'w', newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        if TRANSLATE:
            columns = translate_list(columns, lg_src=SRC_LANG, lg_dest=DEST_LANG)
        writer.writerow(columns)
        for line in lines:
            writer.writerows(line)

def format_technic_info(str):
    """
    Return a string in which '\n' have been inserted before specific substrings listed in TECHNIC_SUB_DATA
    
    Parameters
    ----------
    str : str
        String to transform
    """
    formatted_str = str
    for sub_str in TECHNIC_SUB_DATA:
        try:
            formatted_str = formatted_str.replace(sub_str, '\n' + sub_str)
        except:
            continue
    return formatted_str

def remove_accent(text):
    """
    Return a string in which letters with accents where replaced with corresponding letter without accent

    Parameters
    ----------
    text : str
        String to transform
    """
    text = unicodedata.normalize('NFKD', text)
    text_normalized = "".join([c for c in text if not unicodedata.combining(c)])
    text_normalized = text_normalized.replace("ä", "a")
    return text_normalized
    
if __name__ == '__main__':
    cwd = os.getcwd()
    id_list = []
    base_url = ''
    if GET_COLLECTION:
        id_list = get_columns(RESOURCES_FOLDER + COLLECTION_ID_FILE)
        base_url = COLLECTION_BASE_URL
    else:
        id_list = get_columns(RESOURCES_FOLDER + MUSEUM_ID_FILE)
        base_url = MUSEUM_BASE_URL
    columns = get_columns(RESOURCES_FOLDER + COLUMNS_FILE)
    infos_list = []
    for id in id_list:
        object_url_list = get_objects_url(base_url + id)
        infos = scrap_objects(object_url_list, columns, base_url + id)
        infos_list.append(infos)
    save_to_csv(columns, infos_list, RESOURCES_FOLDER + CSV_RESULTS_FILE)
