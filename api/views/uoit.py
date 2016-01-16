import sys, urllib, re
from api import app
from flask import Blueprint, jsonify
from bs4 import BeautifulSoup as bs

uoit = Blueprint('uoit', __name__)

RMP_URL = "http://www.ratemyprofessors.com"


@uoit.route('/profs', methods=['GET'])
def getProfList():
    URL_BASE = 'https://ssbp.mycampus.ca/prod/www_directory.directory_uoit.p_ShowDepartment?department_name_in='
    DEPARTMENT_CODES = ['U1', 'U2', 'U3', 'U4', 'U7', '7519', '14111']
    profs = set()
    try:
        for code in DEPARTMENT_CODES:
            soup = getSoup(URL_BASE + code)
            rows = soup.find_all('tr', {'class': 'regularText'})
            for row in rows:
                prof = row.find('a').getText().split()
                prof = [name.strip() for name in prof]
                profs.update(specialNameCase(prof))
        return jsonify({'profs': list(profs)}), 200
    except Exception as e:
        print(e)
        return 'No response from server for prof list'


def score_prof(searchSoup, name):
    profURL = getProfileURL(searchSoup)
    profSoup = getSoup(profURL)
    firstReviewer = profSoup.find('div',
                    text = re.compile('Be the first to rate'),
                    attrs={'class':'headline'})
    if firstReviewer:
        return jsonify(createErrorJSON(name, profURL)), 404
    return jsonify(createProfJSON(profURL, name)), 200


@uoit.route('/score/<name>', methods=['GET'])
def try_score(name):
    print(name)
    names = set()
    name = [n.strip() for n in name.split()]
    names.update(specialNameCase(name))

    for test in names:
        searchSoup = getSoup(createSearchURL(test.split()))
        if isSearchResults(searchSoup):
            return score_prof(searchSoup, name)
    return jsonify(createErrorJSON(name)), 404


def createErrorJSON(name, url=False):
    name = ' '.join(name).title()
    message = 'Professor ' + name + ' has not been rated yet.'
    salary = getSalary(name)
    if not url:
        url = 'http://www.ratemyprofessors.com/teacher/create'
        message = ('Professor ' + name + ' does not yet exist on ' +
                   'Rate My Professor.')
    return {'url': url, 'message': message, 'salary':salary}


def createProfJSON(profURL, name):
    soup = getSoup(profURL)
    grades = soup.find_all('div', {'class': 'grade'})[0:3]
    ratings = soup.find_all('div', {'class': 'rating'})[0:3]
    rating_count = soup.find('div', {'class': 'rating-count'})
    hotness_image = ((grades.pop()).find('img')['src']).split('/')[-1]
    grades = [x.getText() for x in grades]
    ratings = [x.getText() for x in ratings]
    return {'name': ' '.join(name),
            'overall_score': grades[0],
            'average_grade': grades[1],
            'hotness_image': hotness_image,
            'helpfulness': ratings[0],
            'clarity': ratings[1],
            'easiness': ratings[2],
            'num_ratings': rating_count.getText().strip(),
            'profile_url': profURL,
            'salary': getSalary(name)}


def getSalary(name):
    sunshine = app.config['SUNSHINE']
    for key, val in sunshine.items():
        if ' '.join(name).upper() == key:
            return val
    return 'N/A'


def getProfileURL(soup):
    prof = soup.find('li', {'class': 'listing PROFESSOR'})
    href = prof.find('a')['href']
    return RMP_URL + href


def isSearchResults(soup):
    noResultsMessage = 'Your search didn\'t return any results'
    div = soup.find('div',
                        text=re.compile(noResultsMessage),
                        attrs={'class': 'result-count'})
    return div is None


def createSearchURL(nameList):
    searchURL = RMP_URL + ("/search.jsp?queryoption=HEADER"
    "&queryBy=teacherName&schoolName=University+of+Ontario"
    "+Institute+of+Technology&schoolID=4714&query=+")

    return searchURL + '+'.join(nameList)


def getSoup(url):
    return bs(urllib.request.urlopen(url).read(), 'html.parser')


def specialNameCase(prof):
    cases = set()
    if len(prof) == 2:
        cases.add(' '.join(prof))
    elif '(' in prof[1]:
        cases.add(prof[0] + ' ' + prof[2])
        cases.add((prof[1])[1:-1] + ' ' + prof[2])
    elif '(' in prof[2]:
        cases.add(prof[0] + ' ' + prof[1])
        cases.add(prof[0] + ' ' + (prof[2])[1:-1])
    elif len(prof) == 3:
        cases.add(prof[0] + ' ' + prof[1] + prof[2])
        cases.add(prof[0] + ' ' + prof[2])
    else:
        cases.add(prof[0] + ' ' + ''.join(prof[1:]))
        cases.add(prof[0] + ' ' + prof[1] + ' ' + ''.join(prof[2:]))
        cases.add(prof[0] + ' ' + ''.join(prof[1:3]) + ' ' + prof[3])
    cases.add(' '.join(prof))
    return cases

