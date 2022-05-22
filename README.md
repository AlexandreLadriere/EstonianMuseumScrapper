# EstonianMuseumScrapper
[![GitHub license](https://img.shields.io/github/license/AlexandreLadriere/EstonianMuseumScrapper.svg)](https://github.com/AlexandreLadriere/EstonianMuseumScrapper/blob/main/LICENSE)

This project aimed at retrieving open source data from Estonian museum collections, in order to put them in a spreadsheet format, and then make analyses on these data.
This project does not handle the data analysis part.

## How it works
This project can work in two different ways

### Retrieving all data from specific collections
Retrieving all data from specific collections, by filling in the collection IDs in the [collection_id.txt] file, and setting the ``GET_COLLECTION`` value to true in the [scrapper.py] script.

In this case, the script browses the list of objects URL (each object url looks like ``http://opendata.muis.ee/object/OBJECT_ID``) of each selected collection (each collection URL looks like ``https://www.muis.ee/rdf/collection/COLLECTION_ID``), and for each object, it retrieves the following information from the page of the object in question (see [columns_et.txt] file for info names), by using [BeautifulSoup]: 
- RdfURL
- ObjectURL
- ImageURL
- Muuseumikogu
- Nimetus
- Number
- Autor
- Hinnang museaali kultuuriväärtuse kohta
- Olemus
- Originaal
- Dateering
- Seisund
- Eritingimused
- Eraldatavad osad

Then, when all the objects have been browsed, and their information stored, this information is then saved as a CSV file, but also as a JSON database (see [TinyDB] for more info).

By default, all results are saved in Estonian, without accents. These results can be translated into English (by using Google Translate API), if the ``TRANSLATE`` variable of the [scrapper.py] script is set to TRUE. However, this will considerably increase the execution time of the script.


### Retrieving all data from specific museums
Retrieving all data from specific museums (all collections), by filling in the museum IDs in the [museum_id.txt] file, and setting the ``GET_COLLECTION`` value to false in the [scrapper.py] script.

In this case, the script goes through each museum (each museum URL looks like ``http://www.muis.ee/rdf/objects-by-museum/MUSEUM_ID``) to get the list of its objects. Then, from each object URL, the operation is the same as the one just above in the case of the first method.

## License
This project is licensed under the MIT License - see the [LICENSE] file for details.

## Contributing
Contributions are welcome :smile:

### Pull requests
Just a few guidelines:
-   Write clean code with appropriate comments and add suitable error handling.
-   Test the application and make sure no bugs/ issues come up.
-   Open a pull request, and I will be happy to acknowledge your contribution after some checking from my side.

### Issues
If you find any bugs/issues, raise an issue.

  [LICENSE]: <LICENSE>
  [scrapper.py]: <https://github.com/AlexandreLadriere/EstonianMuseumScrapper/blob/main/src/scrapper.py>
  [collection_id.txt]: <https://github.com/AlexandreLadriere/EstonianMuseumScrapper/blob/main/resources/collection_id.txt>
  [museum_id.txt]: <https://github.com/AlexandreLadriere/EstonianMuseumScrapper/blob/main/resources/museum_id.txt>
  [columns_et.txt]: <https://github.com/AlexandreLadriere/EstonianMuseumScrapper/blob/main/resources/columns_et.txt>
  [TinyDB]: <https://tinydb.readthedocs.io/en/latest/>
  [BeautifulSoup]: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>
