import requests
import csv

SPECIAL_CHAR = ['\n', '\t']
CHAR_TO_REMOVE = ['\"', '/>']
COLUMNS_FILE = 'columns.txt'
MUSEUM_ID_FILE = 'museum_id.txt'
#MUSEUM_URL = 'http://www.muis.ee/rdf/objects-by-museum/83529'
MUSEUM_BASE_URL = 'http://www.muis.ee/rdf/objects-by-museum/'
#OBJECT_URL = 'http://opendata.muis.ee/object/1858783'
#OBJECT_URL = 'http://opendata.muis.ee/object/1259094'
#OBJECT_BASE_URL = 'http://opendata.muis.ee/object/'
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

# get all info of an object (specified by a xml page), where infos are a list of name to find. result is a list of the size of the given 'info' list
def get_object_info(object_page, info):
    object_info = []
    # go through the page text for each 'info' to get the info balise index
    for info_type in info:
        info_type_balise = '>' + info_type + '<'
        info_type_balise_index = object_page.text.find(info_type_balise)
        # info type does not exits on the given page text
        if info_type_balise_index == -1 :
            object_info.append('')
        else:
            value = ''
            if(object_page.text[info_type_balise_index + len(info_type_balise): info_type_balise_index + len(info_type_balise) + 4] == '/th>'):
                i = info_type_balise_index + len(info_type_balise) + 8
                while object_page.text[i] != '<':
                    value += object_page.text[i]
                    i += 1
            elif (object_page.text[info_type_balise_index + len(info_type_balise): info_type_balise_index + len(info_type_balise) + 6] == '/span>'):
                i = info_type_balise_index + len(info_type_balise) + 6
                while object_page.text[i] != '<':
                    value += object_page.text[i]
                    i += 1
            object_info.append(remove_character(SPECIAL_CHAR, value))
    return object_info

# get thumbnail(s) of the object by looking for a specific balise in the object page text
def get_thumbnail_url(object_page):
    thumbnail_balise = "id=\"thumbnail_"
    thumbnail_url = ''
    split_object_page_text = object_page.text.split(thumbnail_balise)
    if len(split_object_page_text) == 1: # no thumbnail found
        return thumbnail_url
    else:
        for i in range(1, len(split_object_page_text)):
            thumbnail_url += (split_object_page_text[i].split("\"", 3))[2]
            if(i != len(split_object_page_text) - 1):
                thumbnail_url += '\n'
    return thumbnail_url

def save_result(columns_name, object_info_list, file_name):
    file = open(file_name, 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerow(columns_name) 
        write.writerows(object_info_list) 

museum_id_list = get_columns(MUSEUM_ID_FILE)
columns = get_columns(COLUMNS_FILE)
object_info_total_list = []
for museum_id in museum_id_list:
    museum_object_list = []
    museum_object_balise = '<crm:P46_is_composed_of rdf:resource='
    second_split_balise = '/>'
    museum_page = requests.get(MUSEUM_BASE_URL + museum_id)
    museum_page_split = museum_page.text.split(museum_object_balise)
    #for i in range(1, len(museum_page_split)):
    for i in range(1, 10):
        museum_object_list.append(remove_character(CHAR_TO_REMOVE, (museum_page_split[i].split(second_split_balise))[0]))
    for museum_object_url in museum_object_list:
            object_page = requests.get(museum_object_url)
            object_info = get_object_info(object_page, columns)
            object_info[0] = MUSEUM_BASE_URL + museum_id
            object_info[1] = museum_object_url
            object_info[2] = get_thumbnail_url(object_page)
            object_info_total_list.append(object_info)
            print(object_info)
save_result(columns, object_info_total_list, CSV_RESULTS_FILE)

# cas special dimension (utf-8 ?)
# cas pour plusieurs dimensions, (object composé de plusieurs éléments) --> Pas de distinction matériel, dimension, etc ?
# get museum name
# optimiser