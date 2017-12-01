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

# Installation
```
sudo ln -s <path>/<to>/<this>/<repo>/tools/kimaiCSV2PDF/kimai_csv2pdf.py /usr/local/bin
```

# Configuration
To permanently set your own name you can edit the file `myConfig.json` (first copy `demoConfig.json` to `myConfig.json`, then edit).

# Usage
First, you need to export your data via the Kimai export manager.
When you downloaded the `export.csv` file can simply run:
```sh
python kimai_csv2pdf.py -i ~/Downloads/export.csv
```
This should compile the file `zeitaufzeichnung.pdf` in your current working directory

Further comanndline option are displayed when running
```
python kimai_csv2pdf.py -h
```

## Insert scanned signature
To test this feature run:
```
python kimai_csv2pdf.py -i ~/Downloads/export.csv -s demo
```

To use your own signature:
```
python kimai_csv2pdf.py -i ~/Downloads/export.csv -s <path>/<to>/<scanned>/<signature>.jpg
```

# Troubleshooting
It might happen, that the resulting document has some formatting issues (for example the table header). In such occasions manually running
```sh
pdflatex zeitaufzeichnung.tex
```
might fix your problem.
