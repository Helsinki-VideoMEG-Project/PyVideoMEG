# Minimal Sphinx Makefile
# Source in docs/src/, build output in docs/html/html

SPHINXOPTS    ?=
SPHINXBUILD   ?= python -m sphinx
SOURCEDIR     = src
HTMLBUILDDIR  = html

.PHONY: html

html:
	rm -rf "$(HTMLBUILDDIR)"
	@$(SPHINXBUILD) -M "html" "$(SOURCEDIR)" "$(HTMLBUILDDIR)" $(SPHINXOPTS) $(O)
	touch "$(HTMLBUILDDIR)/html/.nojekyll"

clean:
	rm -rf "$(HTMLBUILDDIR)"

