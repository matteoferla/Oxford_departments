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

* My department NDM is huge and contains many units within it hence why it was parsed.
* STRUBI is a unit within a department, but calls itself a division (normally the topmost category)
* The Department of Continuing Education is a division
* The SGC was rebranded as the CMD, but is present in departments-a_z.


