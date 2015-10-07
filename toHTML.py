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
    <link rel="stylesheet" href="style.css" media="screen"/>
    <script type="text/javascript" src="http://culturenumerique.univ-lille3.fr/plugins/jquery/jquery.min.js"></script>
    <script type="text/javascript" src="js/fancybox/jquery.fancybox.pack.js"></script>

    <link rel="stylesheet" href="css/fancybox/jquery.fancybox.css" type="text/css" media="screen" />
"""

FOOTER = """

<footer>
    <a href="https://www.univ-lille3.fr/"><img src="svg/logo_lille3.svg" title="" alt="Lille 3" /></a>
    <p><a href="http://culturenumerique.univ-lille3.fr/" title="Culture Numérique">Culture Numérique</a> - 2015</p>
</footer>
</div> <!-- End of container-->
</body>
</html>
"""

SCRIPTS = """
    \n<!-- SCRIPTs  -->
    <script type="text/javascript">
        $(".fancybox").fancybox({
                            padding : 0,
                            maxWidth : '90%',
                            maxHeight : '90%',
                            fitToView : false,
                            width : '80%',
                            height : '80%',
                            autoSize : false,
                            closeClick : false,
                            openEffect : 'none',
                            closeEffect : 'none',
                            tpl: {
                                    next : '<a title="Next" class="fancybox-nav fancybox-next fancybox-wb-next" href="javascript:;"></a>',
                                    prev : '<a title="Previous" class="fancybox-nav fancybox-prev fancybox-wb-prev" href="javascript:;"></a>',
                                    closeBtn: '<a title="Close" class="fancybox-item fancybox-close fancybox-wb-close" href="javascript:;"></a>'
                            },
                            helpers : {
                                    overlay : {
                                        css : {
                                            'background' : 'rgba(255, 255, 255, 0.95)'
                                        }
                                    }
                            }
                            });
        // control of Navigation and sections loading
        $(function(){
            $(".accordion ul li a").click(function(e){
                e.preventDefault();
                var selector = $(this).attr('data_sec_id');
                console.log('selector', selector);
                if (selector.length == 0) {
                    return true
                }
                else {
                    if ($(this).hasClass('subsection')){
                        $('a.subsection').removeClass('active');
                        $(this).addClass('active');
                    }
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
        // Accordion menu
        (function($) {
            $('.accordion > li:eq(0) a').addClass('active').next().slideDown();

            $('.accordion a.section').click(function(j) {
                console.log("accordéon ====");
                var dropDown = $(this).closest('li').find('p');
                $(this).closest('.accordion').find('p').not(dropDown).slideUp();

                if ($(this).hasClass('active')) {
                    $(this).removeClass('active');
                } else {
                    $(this).closest('.accordion').find('a.active').removeClass('active');
                    $(this).addClass('active');
                }

                dropDown.stop(false, true).slideToggle();
                j.preventDefault();
            });
        })(jQuery);
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
    doc.asis('<div id="container">')
    with tag('header'):
        with tag('h1'):
            with tag('a', klass="maintitle", href="http://culturenumerique.univ-lille3.fr", title="Culture Numérique"):
                text('Culture Numérique')
        with tag('h2'):
            text(data["lom_metadata"]["title"])

    doc.asis('<!--  NAVIGATION MENU -->')
    with tag('nav', klass="menu accordion"):
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
                    with tag('a', href="#", data_sec_id=section_id, klass="section"):
                        text(data["sections"][idA]["title"])
                    with tag('p'):
                        # looping through subsections, skipping non html files
                        for idB, subsection in enumerate(data["sections"][idA]["subsections"]):
                            try:
                                href = data["sections"][idA]["subsections"][idB]["source_file"]
                            except:
                                href = ""
                            try:
                                videos = data["sections"][idA]["subsections"][idB]["videos"]
                            except:
                                videos = []
                            if href.endswith(".html") or len(videos) > 0:
                                subsection_id = "subsec_"+str(idA)+"_"+str(idB)
                                section_type = data["sections"][idA]["subsections"][idB]["type"]
                                with tag('a', href="#", data_sec_id=subsection_id, klass="subsection "+section_type):
                                    text(data["sections"][idA]["subsections"][idB]["title"])

    #print (" ====================  A: Result doc :\n %s" % ((doc.getvalue())))

    doc.asis('<!--  MAIN CONTENT -->')
    with tag('main', klass="content"):
        # Loop through sections
        for idA, section in enumerate(data["sections"]):
            section_id = "sec_"+(str(idA))
            # load intro by default, rest is hidden
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
                with tag('section', id=subsection_id, style="display:none"):
                    try:
                        href = data["sections"][idA]["subsections"][idB]["source_file"]
                    except:
                        href = ""
                        text("")
                    if href.endswith(".html"):
                            try:
                                doc.asis(parse_content(href))
                            except:
                                print (" ---- no web content for subsection %s" % (subsection_id))
                                text("")
                    try:
                        videos = data["sections"][idA]["subsections"][idB]["videos"]
                        for idVid, video in  enumerate(videos):
                            print (" ---- FOUND video content for subsection %s : %s" % (subsection_id, video))
                            try:
                                embed_src = video["video_embed_src"]
                                doc.asis(parse_content(embed_src))
                                doc.asis("\n\n")
                                # add text in fancybox lightbox
                                text_src =  video["video_text_src"]
                                text_id = subsection_id+"_"+str(idVid)
                                with tag('a', klass="inline fancybox", href="#"+text_id):
                                    text('Version Texte')
                                with tag('div', style="display:none"):
                                    with tag('div', id=text_id):
                                        doc.asis(parse_content(text_src))
                            except:
                                print (" ---- error while processsing video content for subsection %s" % (subsection_id))
                                text("")
                    except:
                        print (" ---- NO video content for subsection %s" % (subsection_id))
                        videos = []


    #print ("==================  B:  Result doc :\n %s" % ((doc.getvalue())))
    doc.asis(SCRIPTS)
    doc.asis(FOOTER)
    indexHtml = open('index.html', 'w')
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
    print ("Arguments : filein %s " % (filein))
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
