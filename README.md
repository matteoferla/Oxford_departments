# Oxford_departments
Parsed names of divisions/departments/units of the University of Oxford.

## Reasoning
This is a silly table for use for categorising email address domains on a mailing list.
The problem is that there's no divisions/departments/unit json for the university.

## Code

The code is very simple. See [parser.py](parser.py).

It simply gets the data from, using `requests` and `beautifulsoup`:

* https://www.ox.ac.uk/about/divisions-and-departments
* https://www.ox.ac.uk/about/colleges
* https://www.ndm.ox.ac.uk/institutes-centres-units
* https://www.ox.ac.uk/about/departments-a_z

After that I manually checked what tags to fish out.
.

`departments-a_z` is used to fill the gaps. 
It is out of date however: as a result several units have their names taken from the title tag of their relavant site.

Notes:

My department NDM is huge and contains many units within it hence why it was parsed. 

STRUBI and NDCLS are units within departments, but calls itself a division (normally the topmost category)

The Department of Continuing Education is a division 

The SGC was rebranded as the CMD, but is present in departments-a_z.

`ouh.nhs.uk` was added manually as technically OUH NHS FT is not a departament.

The data is not perfect. So some fixes are required in the data as parsed.
For example, the code did not parse the WIMM, which is part of the Radcliffe Department of Medicine
and not the Nuffield Department of Medicine.

```python3
import requests
from bs4 import BeautifulSoup
from typing import *

def get_department_by_link(address: str) -> Union[str, None]:
    reply = requests.get('https://' + address)
    assert reply.status_code == 200
    soup = BeautifulSoup(reply.text, 'html.parser')
    for link in soup.find_all('a'):  #type: Tag
        if 'title' in link.attrs and 'epartment' in link.attrs['title']:
            return link.attrs['title'].strip()
    return None

# buildings : _the_ pd.DataFrame
i = buildings.loc[buildings.address == 'www.imm.ox.ac.uk'].index[0]
department = get_department_by_link('www.imm.ox.ac.uk')
buildings.at[i, 'department'] = department
```

This trick is rather shoddy as the name may not match
and will not work for all: `www.cardiov.ox.ac.uk` redirects to `RDM`.
I ended up fixing manually (see [parser.py](parser.py)).

The "NDCN" will result in 
"Project to Investigate Memory and Ageing, The Oxford - OPTIMA"
but in reality it is the Nuffield Department of Clinical Neurosciences as
it includes stuff like ophthalmology.

## Email list
Here is an example snippet using the above:

```python3
import pandas as pd

with open('mailing_list.txt') as fh:
    emails = [e.strip() for e in fh.readlines() if e.strip()]

subscribers = pd.DataFrame({'email': emails})
subscribers = pd.concat([subscribers,
                         subscribers.email.str.extract('^(?P<name>.*)@(?P<domain>.*)$')
                        ],
                        axis='columns')
specials = {'har.mrc.ac.uk': 'Harwell MRC', 
            'nhs.net': 'Oxford University Hospitals',
           }

def get_name(domain: str) -> str:
    matches = buildings.loc[buildings.address.str.contains(domain)]
    if len(matches):
        return matches.name.values[0]
    elif domain in specials:
        return specials[domain]
    else:
        raise KeyValue(domain)

def get_department(domain: str) -> str:
    if domain in specials:
        return specials[domain]
    matches = buildings.loc[buildings.address.str.contains(domain)]
    if len(matches) == 0:
        raise KeyValue(domain)
    if 'college' in matches['rank'].values:
        return 'college'
    if 'department' in matches['rank'].values:
        return matches.loc[~matches.name.isna()].name.values[0]
    departments = matches.loc[~matches.department.isna()].department.values
    if len(departments) > 0:
        return departments[0]
    print(matches)
subscribers['unit'] = subscribers.domain.apply(get_name)
subscribers['department'] = subscribers.domain.apply(get_department)
```

