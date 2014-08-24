#! /usr/bin/env python

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, getnames, homogeneize_latex_encoding

preamble = r"""
\documentclass[10pt,a4paper]{moderncv}
\moderncvtheme[green]{classic}
\usepackage[utf8]{inputenc}
\usepackage[scale=0.8]{geometry}
\usepackage{url}
\setlength{\hintscolumnwidth}{1.5cm}
\AtBeginDocument{\recomputelengths}
\firstname{}
\familyname{}
\begin{document}
\section{Publications}
"""

endamble = r"""
\end{document}
"""

phd_preamble = "Dissertation"
journal_preamble = "International peer-reviewed journals"
book_preamble = "Book chapters"
conf_preamble = "International peer-reviewed conference article (6-8 pages)"
short_preamble = "Short peer-reviewed publications"

bp = None

with open("publications.bib", 'r') as bibfile:
    #bp = BibTexParser(bibfile, customization=homogeneize_latex_encoding)
    bp = BibTexParser(bibfile)

publis = bp.get_entry_list()

shorts = sorted([a for a in publis if ('note' in a and 'Short' in a['note'])], key=lambda i: i["year"], reverse = True)

publis = [p for p in publis if p not in shorts]

dissertation = [a for a in publis if a["type"] == "phdthesis"]

confs = sorted([a for a in publis if a['type']  in ['conference', 'inproceedings']], key=lambda i: i["year"], reverse = True)

journals = sorted([a for a in publis if a['type']  in ['article']], key=lambda i: i['year'], reverse = True)

bookchapters = sorted([a for a in publis if a['type']  in ['inbook']], key=lambda i: i['year'], reverse = True)

def format(preamble, items, book = False):
    res  = r"\vspace{1em}\subsection{" + preamble + "}\n"

    if book:
        for i in items:
            res += "\\vspace{0.2em}\\cvlistitem{%s \\\\ \\textbf{%s} \\\\ in:\\textit{%s} %s.}\n" % (i["author"], i["chapter"], i["title"], i["year"])
        return res

    for i in items:
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

        #res += "\\cvlistitem{%s, \\textbf{%s}, \\textit{%s} %s.}\n" % (", ".join(getnames(author(i)["author"])), i["title"], booktitle, i["year"])
        res += "\\vspace{0.2em}\\cvlistitem{%s \\\\ \\textbf{%s} \\\\ \\textit{%s} %s.%s}\n" % (i["author"], i["title"], booktitle, i["year"], pub)

    return res

print(preamble)
print(format(journal_preamble, journals))
print(format(conf_preamble, confs))
print(format(short_preamble, shorts))
print(format(book_preamble, bookchapters, book = True))
print(format(phd_preamble, dissertation))
print(endamble)
