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
    profSoup = getSoup(profURL)
    return jsonify(createProfJSON(profSoup, name)), 200

def createProfJSON(soup, name):
    grades = soup.find_all('div', {'class': 'grade'})[0:3]
    ratings = soup.find_all('div', {'class': 'rating'})[0:3]
    hotness_image = ((grades.pop()).find('img')['src']).split('/')[-1]
    grades = [x.getText() for x in grades]
    ratings = [x.getText() for x in ratings]
    return {'name': ' '.join(name),
            'overall score': grades[0],
            'average grade': grades[1],
            'hotness image': hotness_image,
            'helpfulness': ratings[0],
            'clarity': ratings[1],
            'easiness': ratings[2]}

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
