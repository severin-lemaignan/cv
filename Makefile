
TARGET=cv.tex cv-2p.tex cv-teaching.tex

DOT=$(wildcard figs/*.dot)
SVG=$(wildcard figs/*.svg)

all: paper

$(TARGET:.tex=.pdf): %.pdf: %.tex
	TEXINPUTS=:./sty lualatex $(<)

$(SVG:.svg=.pdf): %.pdf: %.svg
	inkscape --export-pdf $(@) $(<)

%.aux: paper

%.svg: %.dot

	twopi -Tsvg -o$(@) $(<)

bib: $(TARGET:.tex=.aux)

	bibtex $(TARGET:.tex=.aux)

paper: $(TARGET:.tex=.pdf) $(SVG:.svg=.pdf) $(DOT:.dot=.pdf)

clean:
	rm -f *.aux *.log *.snm *.out *.toc *.nav *intermediate *~ *.glo *.ist $(SVG:.svg=.pdf) $(DOT:.dot=.svg) $(DOT:.dot=.pdf)

distclean: clean
	rm -f $(TARGET:.tex=.pdf)
