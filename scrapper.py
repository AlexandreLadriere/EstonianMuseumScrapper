import requests

SPECIAL_CHAR = ['\n', '\t']
COLUMNS_FILE = 'columns.txt'
MUSEUM_URL = 'http://www.muis.ee/rdf/objects-by-museum/83529'
#OBJECT_URL = 'http://opendata.muis.ee/object/1858783'
OBJECT_URL = 'http://opendata.muis.ee/object/1259094'


def remove_character(char_list, str):
    for char in char_list:
        str = str.replace(char, '')
    return str

def get_columns(file):
    file = open(file, 'r')
    lines = file.readlines()
    columns = []
    for line in lines:
        columns.append(remove_character(SPECIAL_CHAR, line))
    return columns

def get_object_info(object_page, info):
    object_info = []
    for info_type in info:
        info_type_balise = '>' + info_type + '<'
        info_type_balise_index = object_page.text.find(info_type_balise)
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

# get thumbnail(s) of the object 
def get_thumbnail_url(object_page):
    thumbnail_balise = "id=\"thumbnail_"
    thumbnail_url = ''
    split_object_page_text = object_page.text.split(thumbnail_balise)
    if len(split_object_page_text) == 1: # no thumbnail found
        return thumbnail_url
    else:
        for i in range(1, len(split_object_page_text)):
            thumbnail_url += (split_object_page_text[i].split("\"", 3))[2] + '\n'
    return thumbnail_url


columns = get_columns(COLUMNS_FILE)
object_page = requests.get(OBJECT_URL)
object_info = get_object_info(object_page, columns)
object_info[1] = OBJECT_URL
object_info[2] = get_thumbnail_url(object_page)
print(object_info)


# cas spécial pour dimensions
# cas pour plusieurs dimensions, (object composé de plusieurs éléments) --> Pas de distinction matériel, dimension, etc ?