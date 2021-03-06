#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,codecs, locale
#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, getnames, convert_to_unicode 

separate_short = True

citelist = False

numbered = False

def usage():
    print(sys.argv[0] + " [--no-shorts] [--cite-list] [--numbered] > list.tex")

for p in sys.argv[1:]:
    if p in ["-h", "--help"]:
        usage()
        sys.exit(1)
    if "no-shorts" in p:
        separate_short = False
    if "cite-list" in p:
        citelist = True
    if "numbered" in p:
        numbered = True


phd_preamble = "Dissertation"
journal_preamble = "International peer-reviewed journals"
book_preamble = "Book chapters"

if separate_short:
    conf_preamble = "International peer-reviewed conference articles (6-8 pages)"
else:
    conf_preamble = "International peer-reviewed conference articles"

short_preamble = "Short peer-reviewed publications"


##############################################
##############################################
tex_preamble = r"""
\documentclass[10pt,a4paper,sans]{moderncv}
\usepackage[utf8]{inputenc} 
\moderncvtheme[green]{classic}
\usepackage[scale=0.8]{geometry}
\usepackage{url}
\usepackage{enumitem} % for enumerate [resume]
\setlength{\hintscolumnwidth}{1.5cm}
\AtBeginDocument{\recomputelengths}
\firstname{Full list of publications}
\familyname{}
%\title{S\'everin Lemaignan}
\begin{document}
\maketitle
\emph{h-index: 26} -- \emph{i-10: 43} -- \emph{Citations: 2750} (source: Google Scholar, checked on 27/12/2020)
"""

tex_endamble = r"""
\end{document}
"""
##############################################
##############################################
html_templates = dict()

html_templates[journal_preamble] = r"""
<li><b><a href="publis/{id}.pdf" alt="Download the PDF version">
{title}</a></b>, <i>{journal}</i>, {year} <a onclick="$('#bibtex_{id}').show('slow');">(show bibtex)</a><br/>
<b>{author}</b>
<pre style="display: none" id="bibtex_{id}">
"""

html_templates[conf_preamble] = r"""
<li><b><a href="publis/{id}.pdf" alt="Download the PDF version">
{title}</a></b>, <i>{booktitle}</i>, {year} <a onclick="$('#bibtex_{id}').show('slow');">(show bibtex)</a><br/>
<b>{author}</b>
<pre style="display: none" id="bibtex_{id}">
"""

html_endamble = r"""
}}
</pre>
</li>
"""
##############################################
##############################################

bp = None

import json

publis = json.load(open("../academia-website/publications.json"))

if separate_short:
    shorts = sorted([a for a in publis if "abstract" in a['type']], key=lambda i: i["year"], reverse = True)
    publis = [p for p in publis if p not in shorts]

dissertation = [a for a in publis if a["type"] == "dissertation"]

confs = sorted([a for a in publis if a['type']  in ['conference', 'inproceedings']], key=lambda i: i["year"], reverse = True)

journals = sorted([a for a in publis if a['type']  in ['journal']], key=lambda i: i['year'], reverse = True)

bookchapters = sorted([a for a in publis if a['type']  in ['chapter']], key=lambda i: i['year'], reverse = True)

def cite_list(preamble, items):
    res  = r"\section{" + preamble + "}\n"
    if numbered:
        res += r"\begin{enumerate}[resume]" + "\n"
    else:
        res += r"\begin{itemize}" + "\n"
    for i in items:
        res += "  \\item \\textbf{%s}~\\cite{%s}\n" % (i["title"], i["id"])

    if numbered:
        res += r"\end{enumerate}" + "\n"
    else:
        res += r"\end{enumerate}" + "\n"
    return res



def tex_format(preamble, items, book = False):

    papers_underreview = []

    res  = r"\vspace{1em}\section{" + preamble + "}\n"

    if numbered:
        res += r"\begin{enumerate}[resume]" + "\n"
    else:
        res += r"\begin{itemize}" + "\n"

    if book:
        for i in items:
            res += "\\item{%s \\\\ \\textbf{%s} \\\\ %s.}\n" % (", ".join(i["authors"]), i["title"], i["year"])

        if numbered:
            res += r"\end{enumerate}" + "\n"
        else:
            res += r"\end{itemize}" + "\n"

        return res

    def render(i):

        booktitle = i["venue"]

        pub = ""
        if 'doi' in i:
            pub +=" DOI:~\\texttt{{\\href{{https://doi.org/{0}}}{{{0}}}}}.".format(i['doi'].replace("_", "\\_"))
        else:
            if 'isbn' in i:
                pub = " ISBN:~%s." % i['isbn']
            elif 'issn' in i:
                pub = " ISSN:~%s." % i['issn']


        if 'note' in i and i['note'] not in ["Short", "Under review"]:
            pub += " %s." % (", ".join([t for t in i['note'].split("Short,") if t]).strip())

        return "\\vspace{0.2em}\\cvlistitem{%s, \\\\ \\textbf{%s}, \\\\ \\textit{%s} %s.%s}\n" % (", ".join(i["authors"]), i["title"], booktitle, i["year"],pub)
        #return "\\item{%s \\\\ \\textbf{%s} \\\\ \\textit{%s} %s.%s}\n" % (", ".join(i["authors"]), i["title"], booktitle, i["year"], pub)


    for i in items:
        if 'note' in i and "not peer-reviewed" in i['note']:
            continue
        if 'note' in i and "Under review" in i['note']:
            papers_underreview.append(i)
            continue
        res += render(i)

    if papers_underreview:
        res  += r"\vspace{1em}\subsection{Under review}" + "\n"

        for i in papers_underreview:
            res += render(i)

    if numbered:
        res += r"\end{enumerate}" + "\n"
    else:
        res += r"\end{enumerate}" + "\n"

    return res

def html_format(preamble, items, book = False):
    res  = r"<h4>" + preamble + "</h4>\n<ul>"

    #if book:
    #    for i in items:
    #        res += "\\vspace{0.2em}\\cvlistitem{%s \\\\ \\textbf{%s} \\\\ in:\\textit{%s} %s.}\n" % (i["author"], i["chapter"], i["title"], i["year"])
    #    return res

    for i in items:
        res += html_templates[preamble].format(**i)

        booktitle = ""
        if 'booktitle' in i:
            booktitle = i["booktitle"]
        elif 'journal' in i:
            booktitle = i["journal"]

        pub = ""
        if 'isbn' in i:
            pub = " ISBN:~%s." % i['isbn']
        elif 'issn' in i:
            pub = " ISSN:~%s." % i['issn']

        if 'note' in i and i['note'] != "Short":
            pub += " %s." % (", ".join([t for t in i['note'].split("Short,") if t]).strip())

        res += i['raw']
        res += html_endamble

    return res + "\n</ul>\n"

#
#@article{{{key},
#author={{Lemaignan, Séverin}},
#title={{Grounding the Interaction: Knowledge Management for Interactive Robots}},
#year={{2013}},
#issn={{0933-1875}},
#journal={{KI - Künstliche Intelligenz}},
#volume={{27}},
#number={{2}},
#doi={{10.1007/s13218-013-0246-3}},
#publisher={{Springer-Verlag}},
#pages={{183-185}},
#

print(tex_preamble)

if citelist:
    sys.stdout.write(cite_list(journal_preamble, journals))
    print(cite_list(conf_preamble, confs))
    if separate_short:
        print(cite_list(short_preamble, shorts))
    print(cite_list(book_preamble, bookchapters))
    print(cite_list(phd_preamble, dissertation))
else:
    sys.stdout.write(tex_format(journal_preamble, journals))
    print(tex_format(conf_preamble, confs))
    if separate_short:
        print(tex_format(short_preamble, shorts))
    print(tex_format(book_preamble, bookchapters, book = True))
    print(tex_format(phd_preamble, dissertation))
print(tex_endamble)

#print(html_format(journal_preamble, journals))
#print(html_format(conf_preamble, confs))
#print(html_format(short_preamble, shorts))
#print(html_format(book_preamble, bookchapters, book = True))
#print(html_format(phd_preamble, dissertation))
