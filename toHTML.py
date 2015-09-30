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

HEADER = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=yes, initial-scale=1.0">
    <link rel="icon" href="http://culturenumerique.univ-lille3.fr/themes/cultnum/img/favicon.png" />
    <link rel="stylesheet" href="reset.css" media="screen"/>
    <link rel="stylesheet" href="style.css" media="screen"/>
    <script type="text/javascript" src="http://culturenumerique.univ-lille3.fr/plugins/jquery/jquery.min.js"></script>
"""

FOOTER = """

<footer>
    <table>
        <tr>
            <td><img src="http://culturenumerique.univ-lille3.fr/themes/cultnum/img/ul3.png" title="" alt="Lille 3" /></td>
            <td><p><a class="maintitle" href="http://culturenumerique.univ-lille3.fr/" title="Culture Numérique">Culture Numérique</a> - 2015 - Site </p</td>
        </tr>
    </table>
</footer>
</body>
</html>
"""


def usage():
    str = """
Usage:
   exporte les fichiers depuis l'arborescence git + fichier de config pour en faire un fichier HTML index.html
   puis comprimer les resources dans une archive /fileout/ exploitable sur un server Web

   toIMS config_filein fileout
"""
    print (str)
    exit(1)


def replaceLink(link):
    """ Replace __BASE__ in urls with base given un config file toIMSconfig.json """
    return link.replace("__BASE__/", '')


def generateIndexHtml(data):
    """ parse data from config file 'toIMSconfig.json' and recreate imsmanifest.xml """
    # FIXME: use same config file as for IMS archive ?

    # create magic yattag triple
    doc, tag, text = Doc().tagtext()

    doc.asis(HEADER)
    # Print the rest of the header
    with tag('title'):
        text(data["lom_metadata"]["title"])
    doc.asis('</head>\n')
    doc.asis('<body>\n')
    doc.asis('<!--  HEADER -->')
    with tag('header'):
        with tag('h1'):
            with tag('a', class="maintitle", href="http://culturenumerique.univ-lille3.fr", title="Culture Numérique"):
                text('Culture Numérique')
        with tag('h2'):
            text(data["lom_metadata"]["title"])

    doc.asis('<!--  NAVIGATION MENU -->')
    with tag('nav', class="menu"):
        with tag('h3'):
            text('Navigation')
        with tag('ul'):
            # looping through sections
            for idA, section in enumerate(data["sections"]):
                try:
                    source_file = data["sections"][idA]["source_file"]
                    section_id = "sec_"+(str(idA))
                except:
                    section_id = ""
                with tag('li'):
                    with tag('h4'):
                        with tag('a', href="#" data_sec_id=section_id):
                            text(data["sections"][idA]["title"])
                    # looping through subsections
                    for idB, subsection in enumerate(data["sections"][idA]["subsections"]):
                        # href = data["sections"][idA]["subsections"][idB]["source_file"]
                        # filename = href.rsplit('/',1)[1]
                        with tag('li'):
                            with tag('p'):
                                subsection_id = "subsec_"+str(idA)+"_"+str(idB)
                                with tag('a', href="#" data_sec_id=subsection_id):
                                    text(data["sections"][idA]["subsections"][idB]["title"])


    doc.asis('<!--  MAIN CONTENT -->')
    with tag('main', class="content"):
        for idA, section in enumerate(data["sections"]):
            section_id = "sec_"+(str(idA))

            if idA == 0:
                display = "true"
            else:
                display = "false"
            with tag('section', id=section_id style="display:"+display):
                try:
                    href = data["sections"][idA]["source_file"]
                    
                except:


            for idB, subsection in enumerate(data["sections"][idA]["subsections"]):

    # doc.asis("</manifest>")
    # imsfile = open('imsmanifest.xml', 'w')
    # imsfile.write(indent(doc.getvalue()))
    # imsfile.close()
    # return True


def main(argv):
    """ toIMS is a utility to help building imscc archives for exporting curent material to Moodle """
    if len(sys.argv) != 3:
        usage()

    filein = sys.argv[1]
    fileout = sys.argv[2]
    # add .zip if not there
    if fileout.rsplit('.', 1)[1] != 'zip':
        fileout += '.zip'

    # load data from filin
    with open(filein, encoding='utf-8') as data_file:
        data = json.load(data_file)
    # parse data and generate imsmanifest.xml
    generateIMSManifest(data)
    print (" imsmanifest.xml saved. Compressing archive in %s " % (os.getcwd()))

    # Compress relevant files
    zipf = zipfile.ZipFile(fileout, 'w')
    zipf.write(os.getcwd()+'/imsmanifest.xml')
    for dir_name in data['directories_to_ims']:
        for file in os.listdir(dir_name):
            filepath = os.path.join(os.getcwd(), dir_name)
            filepath = os.path.join(filepath, file)
            print (" Adding %s to archive " % (filepath))
            zipf.write(filepath)

    zipf.close()


############### main ################
if __name__ == "__main__":
    main(sys.argv)
