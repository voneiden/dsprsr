import argparse
import json
from xml.etree.ElementTree import parse, Element, tostring, fromstring
import re

re_multi_whitespace = r'\s{2,}'


def process_file(args):
    input_filename = args.input
    output_filename = args.output
    height_fuzz = int(args.height_fuzz)
    with open(input_filename, 'r', errors='replace') as f:
        input_raw = f.read()#.replace(b'�', b'')
    #tree = parse(input_filename)
    root = fromstring(input_raw)
    #root = tree.getroot()
    #print(root)
    pages = []
    document_rows = []
    page_node: Element
    for page_number, page_node in enumerate(root):
        page_rows = []
        last_top = -10
        last_right = -10
        row = []
        if page_node.tag != 'page':
            #print(f'Skip tag {page_node.tag}')
            continue
        #print('PAGE', page_node.attrib)
        text_node: Element
        for text_node in page_node:
            if text_node.tag != "text":
                #print(f"Skip tag {text_node.tag}")
                continue

            raw_str = tostring(text_node, encoding='unicode', method='text')
            raw_str = raw_str.replace('\u2013', '-').replace('\u2000', ' ').replace('\u2022', '*').replace('\u2018', "'").replace('\u2019', "'").strip('\n')
            top = int(text_node.attrib.get('top'))
            left = int(text_node.attrib.get('left'))
            right = left + int(text_node.attrib.get('width'))
            if abs(top - last_top) > height_fuzz:
                # print("new top", top)
                if row:
                    page_rows.append(row)
                    #print(row)

                last_top = top
                last_right = -10
                row = []

            # width fuzz allows us to deposit the string in the same column as the previous one

            if len(row) and (left - last_right) <= 2 and row[-1][-1] != ' ':
                row[-1] = row[-1] + raw_str
            else:
                row.append(raw_str)
            last_right = right

        if row:
            page_rows.append(row)
            #print(row)


        row_t = len(page_rows)

        document_rows += [{'_metadata': {
            'page': page_number+1,
            'row_i': i,
            'row_t': row_t
        }, 'cols': [col.strip() for col in r]} for i, r in enumerate(page_rows)]
        #pages.append({'page_number': page_number+1, 'rows': page_rows})

    with open(output_filename, 'w') as f:
        json.dump(document_rows, f, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--height-fuzz', default=5, dest='height_fuzz')
    args = parser.parse_args()
    process_file(args)
