#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import zipfile
import random

from lxml import etree
from lxml import html
from pprint import pprint
from yattag import indent
from yattag import Doc

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


def generateIMSManifest():
    """ parse config file toIMSconfig.json and recreate imsmanifest.xml """

    with open('toIMSconfig.json', encoding='utf-8') as data_file:
        data = json.load(data_file)
    #pprint(data)

    # create magic yattag triple
    doc, tag, text = Doc().tagtext()
    # open tag 'manifest' with default content:
    doc.asis('<?xml version="1.0" encoding="UTF-8"?><manifest xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" identifier="M_3E1AEC6D" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd">')

    with tag('metadata'):
        with tag('schema'):
            text('IMS Common Cartridge')
        with tag('schemaversion'):
            text('1.1.0')
        with tag('lomimscc:lom'):
            with tag('lomimscc:general'):
                with tag('lomimscc:title'):
                    with tag('lomimscc:string', language=data["lom_metadata"]["language"]):
                        text(data["lom_metadata"]["title"])
                with tag('lomimscc:language'):
                    text(data["lom_metadata"]["language"])
                with tag('lomimscc:description'):
                    doc.stag('lomimscc:string', language=data["lom_metadata"]["language"])
                with tag('lomimscc:identifier'):
                    with tag('lomimscc:catalog'):
                        text('category')
                    with tag('lomimscc:entry'):
                        text(data["lom_metadata"]["category"])

    with tag('organizations'):
        with tag('origanization', identifier="organization0", structure='rooted-hierarchy'):
            with tag('item', identifier='root'):
                for idx, section in enumerate(data["sections"]):
                    section_id = "sec_"+(str(idx))
                    with tag('item', identifier=section_id):
                        with tag('title'):
                            text(str(idx))
                        for index, subsection in enumerate(data["sections"][idx]["subsections"]):
                            with tag('item', identifier=("subsec_"+str(idx)+"_"+str(index)), identifierref=("doc_"+str(idx)+"_"+str(index))):
                                with tag('title'):
                                    text(data["sections"][idx]["subsections"][index]["title"])


    print (indent(doc.getvalue()))

def main(argv):
    """ toIMS is a utility to help building imscc archives for exporting curent material to Moodle"""
    if len(sys.argv) != 3:
        usage()

    dirin = sys.argv[1]
    fileout = sys.argv[2]

    generateIMSManifest()

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
