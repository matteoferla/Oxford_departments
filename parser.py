import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import *
from bs4.element import Tag

clean_address: Callable[[Tag], str] = lambda link: re.search(':?\/\/([\w\.\-]+)',
                                                             link.attrs['href']).group(1)
departments = []

# ## Parse divisions

reply = requests.get('https://www.ox.ac.uk/about/divisions-and-departments')
assert reply.status_code == 200
soup = BeautifulSoup(reply.text, 'html.parser')

for division_header in soup.find_all('h2'):  # type: Tag
    division_name = division_header.getText()
    if 'Division' not in division_name:  # no conted: see below.
        continue
    division_name, division_address = re.search(r'(.*) \((.*)\)', division_name).groups()
    # ## Parse division
    departments.append(dict(name=division_name,
                            address=division_address,
                            rank='division'
                            )
                       )
    # ## Parse departments within
    for department in division_header.fetchNextSiblings()[0].children:  # type: Tag
        link: Tag = department.find('a')
        departments.append(dict(name=department.getText(),
                                division=division_name,
                                address=clean_address(link),
                                rank='department'
                                )
                           )
# this caused issues:
departments.append(dict(name='Continuing Education, Department for',
                        address='www.conted.ox.ac.uk',
                        rank='department'
                        )
                   )

# ## Parse colleges

reply = requests.get('https://www.ox.ac.uk/about/colleges')
assert reply.status_code == 200
soup = BeautifulSoup(reply.text, 'html.parser')
for link in soup.find('table').find_all('a'):  # type: Tag
    departments.append(dict(name=link.getText(),
                            address=clean_address(link),
                            rank='college')
                       )


# ## Parse NDM

def get_better_name(address: str, name: str) -> str:
    try:
        reply = requests.get('https://' + address)
        assert reply.status_code == 200
        title = BeautifulSoup(reply.text, 'html.parser') \
            .find('title') \
            .getText()
        parts = title.translate({ord(k): ord('|') for k in ('—', '–', '-')}).split('|')
        parts = map(str.strip, parts)
        return sorted(parts, key=lambda p: len(p))[-1]
    except Exception as error:
        print(f'{error.__class__.__name__}: {error}')
        return name


reply = requests.get('https://www.ndm.ox.ac.uk/institutes-centres-units')
assert reply.status_code == 200
soup = BeautifulSoup(reply.text, 'html.parser')
for img in soup.find_all('img'):
    link: Tag = img.fetchParents()[1]
    if 'href' not in link.attrs:
        continue
    address: str = clean_address(link)
    if address == 'www.ndm.ox.ac.uk':
        continue
    name = img.attrs['alt']
    if len(name) < 10:
        name = get_better_name(address, name)
    departments.append(dict(name=name,
                            department='Clinical Medicine, Nuffield Department of',
                            division='Medical Sciences Division',
                            address=address,
                            rank='unit'
                            )
                       )

# <img data-copyright-style="inverted" src="https://www.ndm.ox.ac.uk/images/about/copy_of_ndm.jpg" title="copy_of_ndm.jpg" data-mce-src="resolveuid/77eeb90459f8424187e16557a8c60f7e" data-src="https://www.ndm.ox.ac.uk/images/about/copy_of_ndm.jpg" alt="NDM">

# ## Fix
# the link https://www.ox.ac.uk/about/departments-a_z does not list divisions.
# but has better names
missing = []

reply = requests.get('https://www.ox.ac.uk/about/departments-a_z')
assert reply.status_code == 200
soup = BeautifulSoup(reply.text, 'html.parser')
for div in soup.find_all('div'):  # type: Tag
    # only bs4.12 on 3.8 has class_ selector!
    if 'class' in div.attrs and 'description' in div.attrs['class']:
        for link in div.find_all('a'):  # type: Tag
            address = clean_address(link)
            name = link.getText()
            for department in departments:
                if department['address'] != address:
                    continue
                elif len(department['name']) < len(name):
                    department['name'] = name
                    break
                else:
                    break
            else:
                departments.append(dict(name=name,
                                        address=address))

df = pd.DataFrame(departments)
df.to_csv('Oxford_departments.csv')
df.to_json('Oxford_departments.json')
