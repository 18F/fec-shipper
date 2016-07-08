import requests
import json
import sys
import os
from datetime import datetime

# local, feature, dev, stage or prod
env = sys.argv[1] if len(sys.argv) > 1 else 'local'

if env == 'local' or env == 'dev' or env == 'feature':
    list_regs_url = 'https://fec-stage-eregs.18f.gov/api/regulation'
else:
    list_regs_url = 'https://fec-%s-eregs.18f.gov/api/regulation' % env

reg_versions = requests.get(list_regs_url).json()['versions']
print(reg_versions)

regs = {}
for reg in reg_versions:
    if '2016-annual' in reg['version']:
        regs[reg['regulation']] = reg

for reg in reg_versions:
    if reg['regulation'] not in regs:
        by_date = datetime.strptime(reg['by_date'], "%Y-%m-%d")
        most_recent = datetime.strptime(regs[reg['by_date']], "%Y-%m-%d") \
            if reg['by_date'] in regs else datetime(1900, 1, 1)
        if by_date > most_recent:
            regs[reg['regulation']] = reg
        print(reg)

print('total regs: %d' % len(regs))

reg_versions = regs.values()

annual_count = 0
for reg in reg_versions:
    if '2016-annual' in reg['version']:
        annual_count += 1

print('annual count: %d' % annual_count)


def get_sections(reg):
    sections = {}

    for node in reg['children'][0]['children']:
        sections[tuple(node['label'])] = {'text': get_text(node),
                                          'title': node['title']}

    return sections


def get_text(node):
    text = ''
    if "text" in node:
        text = node["text"]

    for child in node["children"]:
        text += ' ' + get_text(child)

    return text


def get_regs():
    for reg in reg_versions:
        if env == 'local' or env == 'dev' or env == 'feature':
            url = 'https://fec-stage-eregs.18f.gov/api/regulation/%s/%s' \
                % (reg['regulation'], reg['version'])
        else:
            url = 'https://fec-%s-eregs.18f.gov/api/regulation/%s/%s' \
                % (env, reg['regulation'], reg['version'])

        regulation = requests.get(url).json()
        sections = get_sections(regulation)
        docs = []
        for section_label in sections:
            doc_id = '%s_%s_%s' % (section_label[0], section_label[1],
                                   reg['version'])
            section_formatted = '%s-%s' % (section_label[0], section_label[1])
            reg_url = '/regulations/{0}/{1}#{0}'.format(section_formatted,
                                                        reg['version'])
            no = '%s.%s' % (section_label[0], section_label[1])
            name = sections[section_label]['title'].split(no)[1].strip()
            doc = {"doc_id": doc_id, "name": name,
                   "text": sections[section_label]['text'], 'url': reg_url,
                   "no": no}

            docs.append(doc)

        yield docs


for docs in get_regs():
    if env == 'local':
        url = 'http://localhost:5000/v1/load/legal/'
    if env == 'dev' or env == 'feature':
        url = 'https://fec-%s-api.18f.gov/v1/load/legal/' % env
    if env == 'stage':
        url = 'https://fec-stage-api.18f.gov/v1/load/legal/'
    if env == 'prod':
        url = 'https://api.open.fec.gov/v1/load/legal/?api_key=%s' \
                    % os.environ['FEC_API_KEY']
    data = {'doc_type': 'regulations', 'docs': docs,
            'api_key': os.environ['FEC_API_KEY']}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    result = r.json()
    print(result)
    if not result['success']:
        print(result)


print(reg_versions)
print('done.')
