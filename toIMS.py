#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import zipfile

from lxml import etree
from lxml import html
from pprint import pprint


def usage():
    str = """
Usage:
   exporte les fichiers depuis l'arborescence git pour les comprimer dans une archive .imscc.

   toIMS dirin fileout
"""
    print (str)
    exit(1)


def replaceLink(link):
    """ Replace __BASE__ in urls with base given un config file toIMSconfig.json """
    return link.replace("__BASE__/", data["base_url"])


def convert(filein, fileout):

    tree = html.fromstring(filein)
    cleaner(tree)

    body = tree.find('body')

    body.rewrite_links(replaceLink)
    f = open(fileout,"wb")
    f.write(html.tostring(body))
    f.close()


def main(argv):
    """ toIMS is a utility to help building imscc archives for exporting curent material to Moodle"""
    if len(sys.argv) != 3:
        usage()

    with open('toIMSconfig.json', encoding='utf-8') as data_file:
        data = json.load(data_file)
    pprint(data)

    dirin = sys.argv[1]
    fileout = sys.argv[2]


    # with zipfile.ZipFile(dirin,'r') as myzip:
    #     for orig in myzip.namelist():
    #         print(orig)
    #         dest = os.path.join(dirout,orig)
    #         if orig.endswith('/'):
    #             os.makedirs(dest,exist_ok=True)
    #         elif orig.endswith(".html"):
    #             f = myzip.read(orig)
    #             convert(f,dest)
    #         else :
    #             myzip.extract(orig,dirout)


############### main ################
if __name__ == "__main__":
    main(sys.argv)
