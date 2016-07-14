import csv
import requests
import json
import sys
import os

# local, feature, dev, stage or prod
env = sys.argv[1] if len(sys.argv) > 1 else 'local'

csv.field_size_limit(10000000)

f = open('data/AO.txt')
reader = csv.reader(f, delimiter=',', quotechar='"')

i = 0
ao_data = {}
for row in reader:
    if i == 2:
        ao_header = row
    if i > 2 and len(row) == len(ao_header):
        ao_data[row[ao_header.index('AO_ID')]] = row
    i += 1

f = open('data/DOCUMENT.txt')

reader = csv.reader(f, delimiter=',', quotechar='"')


def get_docs():
    docs = []
    i = 0
    for row in reader:
        if i == 2:
            header = row
        if i > 2:
            try:
                ao = ao_data[row[header.index('AO_ID')]]
                pdf_url = 'http://saos.fec.gov/aodocs/%s.pdf' \
                    % ao[ao_header.index('AO_NO')]

                doc = {"doc_id": row[header.index('DOCUMENT_ID')],
                       "text": row[header.index('OCRTEXT')],
                       "description": row[header.index('DESCRIPTION')],
                       "category": row[header.index('CATEGORY')],
                       "id": row[header.index('AO_ID')],
                       "name": ao[ao_header.index('NAME')],
                       "summary": ao[ao_header.index('SUMMARY')],
                       "tags": ao[ao_header.index('TAGS')],
                       "no": ao[ao_header.index('AO_NO')],
                       "url": pdf_url}
                docs.append(doc)
            except:
                print(row)

        i += 1

        if i % 20 == 0:
            print('loading doc batch up to %d' % i)
            yield docs
            docs = []
    print('loading doc batch up to %d' % i)
    yield docs

print('loading data into %s...' % env)
for docs in get_docs():
    if env == 'local':
        url = 'http://localhost:5000/v1/load/legal/'
    else:
        url = 'https://fec-%s-api.18f.gov/v1/load/legal/' % env

    data = {'doc_type': 'advisory_opinions', 'docs': docs,
            'api_key': os.environ['FEC_API_KEY']}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    result = r.json()
    if not result['success']:
        print(result)

print('done.')
