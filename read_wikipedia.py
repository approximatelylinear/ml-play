import argparse
import json
import re

import xml.etree.ElementTree as ET

def parse_markup(text):
    # Replace {{ x | y }} with y
    text = re.sub(r'\{\{.*?\|(.*?)\}\}', r'\1', text)

    # Replace [[ x | y ]] with y
    text = re.sub(r'\[\[.*?\|(.*?)\]\]', r'\1', text)

    # Replace [[x]] with x
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)

    # Replace '''x''' with x
    text = re.sub(r'\'\'\'(.*?)\'\'\'', r'\1', text)

    # Replace {{x}} with ''
    text = re.sub(r'\{\{.*?\}\}', '', text)

    # Replace {| x |} with ''
    text = re.sub(r'\{\|.*?\|\}', '', text)

    # Replace date=Month Year with ''
    text = re.sub(r'date=\w+ \d{4}', '', text)

    # Ignore all text if it starts with #
    text = re.sub(r'^#.*', '', text, flags=re.MULTILINE|re.DOTALL)

    # Replace <ref>...</ref> with ''
    text = re.sub(r'<ref>.*?</ref>', '', text, flags=re.DOTALL)

    # Replace <!-- ... --> with ''
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    return text


def parse_passage(text):
    m = re.search(r'==(?P<title>.*)==', text)
    if m:
        title = m.group('title').strip()
    else:
        title = None
    text = re.sub(r'==.*==', '', text)
    return {
        'title': title,
        'text': text.strip()
    }


def parse_wikipedia_dump(xml_file, limit=None, output_file=None):
    # Create an ElementTree object from the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    output = []

    # Iterate over each page element in the XML
    for (page_num, page) in enumerate(root.findall('{http://www.mediawiki.org/xml/export-0.10/}page')):
        if page_num and page_num % 1000 == 0:
            print(f'Processed {page_num} pages')

        title = page.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
        text = page.find('{http://www.mediawiki.org/xml/export-0.10/}revision').find('{http://www.mediawiki.org/xml/export-0.10/}text').text

        text = parse_markup(text)
        if not text:
            continue

        passages = re.split(r'\n{2,}', text)
        passages = [parse_passage(passage) for passage in passages]
        passages = [
            {
                'article_title': title,
                'passage_title': passage['title'],
                'passage': passage['text']
            }
            for passage in passages
            if passage['text']
        ]
        output.extend(passages)

        # You can process or store the title and text in any way you need here
        if page_num >= limit:
            break

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a Wikipedia XML dump')
    parser.add_argument('xml_file', type=str, help='Path to the Wikipedia XML dump file')
    parser.add_argument('--output_file', default=None, type=str, help='Path to the output file')
    parser.add_argument('--limit', default=None, type=int, help='Limit the number of pages to parse')
    args = parser.parse_args()

    parse_wikipedia_dump(args.xml_file, limit=args.limit, output_file=args.output_file)

