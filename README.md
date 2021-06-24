# dsprsr
Exploratory work on parsing Atmel microprocessor datasheet(s) and using the information gained to enrich the Atmel atdef files.

## Steps to process a datasheet

0) `0-atdef2json.py ATtiny814.atdf ATtiny814.atdf.json` to create the base json schema
1)  `pdftohtml -xml -i ATtiny814.pdf ATtiny814.pdf.xml` to convert datasheet into xml
2) `1-xml2json.py ATtiny814.pdf.xml ATtiny814.pdf.json` to convert xml into json file in which text is hopefully grouped by lines
3) `3-json2regdat.py ATtiny814.pdf.json ATtiny814.atdf.json output/ATtiny814.json` to enrich the json schema with datasheet information 

## Height fuzz values

For the ATtiny814 spec sheet, use fuzz of 6
