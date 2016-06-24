import requests
import json
import sys
import os

# local, feature, dev, stage or prod
env = sys.argv[1] if len(sys.argv) > 1 else 'local'

if env == 'local' or env == 'dev':
    list_regs_url = 'https://fec-stage-eregs.18f.gov/api/regulation'
else:
    list_regs_url = 'https://fec-%s-eregs.18f.gov/api/regulation' % env

reg_versions = requests.get(list_regs_url).json()['versions']


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
        if env == 'local' or env == 'dev':
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
    else:
        url = 'https://fec-%s-api.18f.gov/v1/load/legal/' % env
    data = {'doc_type': 'regulations', 'docs': docs,
            'api_key': os.environ['FEC_API_KEY']}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r)
    result = r.json()
    if not result['success']:
        print(result)

print('done.')
