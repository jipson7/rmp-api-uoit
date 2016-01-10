import sys, urllib, re
from api import app
from flask import Blueprint, jsonify
from bs4 import BeautifulSoup as bs

uoit = Blueprint('uoit', __name__)

RMP_URL = "http://www.ratemyprofessors.com"

@uoit.route('/score/<name>', methods=['GET'])
def score_prof(name):
    name = name.split()
    searchSoup = getSoup(createSearchURL(name))
    if not isSearchResults(searchSoup):
        return 'No data', 404
    profURL = getProfileURL(searchSoup)
    return jsonify(createProfJSON(profURL, name)), 200

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
            'profile_url': profURL}

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
