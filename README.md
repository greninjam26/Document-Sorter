# Document-Sorter

This Python project finds PDF files, reads a barcode beginning with `SAL`, renames each PDF to the barcode value, and moves it to a destination folder.
Files that cannot be processed will be moved to an error folder, and every result will be written to a log.

Requires Python 3.10 or newer.

## Project functions

1. **PDF discovery:** validate the source folder and find all the PDFs.
2. **Barcode extraction:** read each PDF and locate its barcode.
3. **Barcode validation:** accept exactly one distinct value beginning with uppercase `SAL` per file.
4. **Rename and move:** rename the PDF and move it to the destination folder.
5. **Error handling:** move PDF files with errors into the destination error folder.
6. **Logging:** log the outcome and reason for every file.

## Run

Install the barcode-reading dependencies once:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then scan a folder:

```bash
python main.py /path/to/starting-folder
```

The starting folder is required. If it is omitted, the program will return an error.

## Test

```bash
python3 -m unittest discover
```

## Structure

```text
document_sorter/  Application code
tests/            Automated tests
main.py           Program entry point
```
