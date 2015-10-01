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
    <img src="http://culturenumerique.univ-lille3.fr/themes/cultnum/img/ul3.png" title="" alt="Lille 3" />
    <p><a href="http://culturenumerique.univ-lille3.fr/" title="Culture Numérique">Culture Numérique</a> - 2015</p>
</footer>
</body>
</html>
"""

SCRIPTS = """
    \n<!-- SCRIPTs  -->
        <script type="text/javascript">
            // control of Navigation and sections loading
            $(function(){
                $("#accordion ul li a").click(function(e){
                    e.preventDefault();
                    var selector = $(this).attr('data_sec_id');
                    console.log('selector', selector);
                    if (selector.length == 0) {
                        return true
                    }
                    else {
                        $('section').hide();
                        var iframe = $('#'+selector).find('iframe');
                        console.log("found iframe ?", iframe)
                        if (iframe.data('src')){ // only do it once per iframe
                            iframe.prop('src', iframe.data('src')).data('src', false);
                            console.log("iframe src = ", iframe.attr('src'))
                            }
                        $('#'+selector).show();

                    }
                    });
            });

            // Accordion script

            $(function () {
                var children = $('#accordion li a').filter(function () {
                    return $(this).nextAll().length > 0
                })
                $('<span class="toChild"></span>').insertAfter(children)
                $('#accordion .toChild').on('click touch', function (e) {
                    $(this).toggleClass("down").next().slideToggle(400);
                    $(this).closest('li').siblings().find('ul').hide()
                });
            })
        </script>\n\n
"""

def usage():
    str = """
Usage:
   exporte les fichiers depuis l'arborescence git + fichier de config pour en faire un fichier HTML index.html
   puis comprimer les resources dans une archive /fileout/ exploitable sur un server Web

   toIMS config_filein
"""
    print (str)
    exit(1)


def replaceLink(link):
    """ Replace __BASE__ in urls with base given un config file toIMSconfig.json """
    return link.replace("__BASE__/", '')

def parse_content(href):
    """ open file and replace ../img with img and src to data_src for iframes """

    myparser = etree.HTMLParser(encoding="utf-8")
    with open(href, 'r') as file:
        htmltext = file.read()

    tree = etree.HTML(htmltext, parser=myparser)
    # = html.fromstring(filein)
    try:
        imgs = tree.xpath('//img')#we get a list of elements
        for img in imgs:
            new_src = img.get('src').replace('../img', 'img')
            img.set('src', new_src)
    except Exception as e:
        pass
    try:
        iframes = tree.xpath('//iframe')
        for iframe in iframes:
            iframe.attrib['data-src'] = iframe.attrib['src']
            etree.strip_attributes(iframe, 'src')
    except Exception as e:
        pass

    return html.tostring(tree, encoding='utf-8').decode('utf-8')


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
            with tag('a', klass="maintitle", href="http://culturenumerique.univ-lille3.fr", title="Culture Numérique"):
                text('Culture Numérique')
        with tag('h2'):
            text(data["lom_metadata"]["title"])

    doc.asis('<!--  NAVIGATION MENU -->')
    with tag('nav', klass="menu", id="accordion"):
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
                    with tag('a', href="#", data_sec_id=section_id):
                        text(data["sections"][idA]["title"])
                    # looping through subsections, skipping non html files
                    for idB, subsection in enumerate(data["sections"][idA]["subsections"]):
                        href = data["sections"][idA]["subsections"][idB]["source_file"]
                        if href.endswith(".html"):
                            with tag('li'):
                                subsection_id = "subsec_"+str(idA)+"_"+str(idB)
                                with tag('a', href="#", data_sec_id=subsection_id):
                                    text(data["sections"][idA]["subsections"][idB]["title"])

    print (" ====================  A: Result doc :\n %s" % ((doc.getvalue())))

    doc.asis('<!--  MAIN CONTENT -->')
    with tag('main', klass="content"):
        # Loop through sections
        for idA, section in enumerate(data["sections"]):
            section_id = "sec_"+(str(idA))
            # load intro by default
            if idA == 0:
                display = "true"
            else:
                display = "none"
            with tag('section', id=section_id, style=("display:"+display)):
                try:
                    href = data["sections"][idA]["source_file"]
                    doc.asis(parse_content(href))
                except:
                    print (" ---- no content for section %s" % (section_id))
                    text("")
            # Loop through subsections
            for idB, subsection in enumerate(data["sections"][idA]["subsections"]):
                subsection_id = "subsec_"+str(idA)+"_"+str(idB)
                href = data["sections"][idA]["subsections"][idB]["source_file"]
                if href.endswith(".html"):
                    with tag('section', id=subsection_id, style="display:none"):
                        try:

                            doc.asis(parse_content(href))
                        except:
                            print (" ---- no content for subsection %s" % (subsection_id))
                            text("")


    print ("==================  B:  Result doc :\n %s" % ((doc.getvalue())))
    doc.asis(SCRIPTS)
    doc.asis(FOOTER)
    indexHtml = open('index_test.html', 'w')
    indexHtml.write(indent(doc.getvalue()))
    indexHtml.close()
    return True


def main(argv):
    """ toIMS is a utility to help building imscc archives for exporting curent material to Moodle """
    if len(sys.argv) != 2:
        usage()

    filein = sys.argv[1]
    # fileout = sys.argv[2]
    # add .zip if not there
    # if fileout.rsplit('.', 1)[1] != 'zip':
    #     fileout += '.zip'

    # load data from filin
    with open(filein, encoding='utf-8') as data_file:
        data = json.load(data_file)

    # print(" Data loaded \n %s" % (data) )
    # parse data and generate imsmanifest.xml
    generateIndexHtml(data)
    print (" index.html saved. Compressing archive in %s " % (os.getcwd()))

    # Compress relevant files
    # zipf = zipfile.ZipFile(fileout, 'w')
    # zipf.write(os.getcwd()+'/imsmanifest.xml')
    # for dir_name in data['directories_to_ims']:
    #     for file in os.listdir(dir_name):
    #         filepath = os.path.join(os.getcwd(), dir_name)
    #         filepath = os.path.join(filepath, file)
    #         print (" Adding %s to archive " % (filepath))
    #         zipf.write(filepath)
    #
    # zipf.close()


############### main ################
if __name__ == "__main__":
    main(sys.argv)
