# dsprsr
Desperate attempt to break down pdf datasheets (from Atmel) into more machine 
readable format.

## Steps to process a datasheet

0) `0-atdef2json.py ATtiny814.atdf ATtiny814.json` to create the base json schema
1)  `pdftohtml -xml -i input.pdf output.xml` to convert datasheet into xml
2) `1-xml2json.py output.xml output.json` to convert xml into json file in which text is hopefully grouped by lines
3) `2-json2regdat.py ATtiny814.json output.json` to enrich the json schema with datasheet information 


## Height fuzz values

For the ATtiny814 spec sheet, use fuzz of 6
