import os, sys
from urllib import request
from bs4 import BeautifulSoup as bs

URL = "http://www.fin.gov.on.ca/en/publications/salarydisclosure/pssd/orgs-tbs.php?year=2014&organization=universities&page="

output = 'sunshine-uoit.csv'
if os.path.isfile(output):
    sys.exit('Output file, sunshine-uoit.csv, already exists. Move or delete it.')

f = open(output, 'w')

UOIT = 'University of Ontario Institute of Technology'

for x in range(1, 5):
    soup = bs(request.urlopen(URL + str(x)).read(), 'html.parser')
    rows = soup.find('table', {'summary': 'Salary Disclosure'})\
               .find('tbody').findAll('tr')
    for row in rows:
        cells = row.findAll('td')
        if UOIT not in cells[0].find('span'):
            continue
        output_row = ''
        for cell in cells:
            if cell.find('span'):
                data = cell.find('span').getText() +','
            else:
                data = cell.getText() + ','
            output_row += data.strip()
        output_row += '\n'
        f.write(output_row)

f.close()

