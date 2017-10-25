# Introduction

This script is used to convert .csv files (exported by [Kimai](http://www.kimai.org/)) to .pdf documents

# Installation

## Requirements
```sh
# TeXLive-Distribution
sudo apt install texlive
sudo apt install texlive-latex-extra
sudo apt install latexmk

# pylatex
sudo apt install python-pip
sudo pip install PyLaTeX
```

# Usage
First, you need to export your data via the Kimai export manager.
When you downloaded the `export.csv` file can simply run:
```sh
python kimai_csv2pdf.py -i ~/Downloads/export.csv
```
This should compile the file `zeitaufzeichnung.pdf` in your current working directory

# Troubleshooting
It might happen, that the resulting document has some formatting issues (for example the table header). In such occasions manually running
```sh
pdflatex zeitaufzeichnung.tex
```
might fix your problem.
