import requests
from lxml import html
import string
import pygal

def getYelpReviewInfo(link="https://www.yelp.com/biz/alchemist-bar-and-lounge-san-francisco?osq=Bars"):
    link = link.strip()
    response = requests.get(link)
    root = html.fromstring(response.content)
    pageid = root.xpath('//div[@id="super-container"]')[0]
    reviewlist = pageid.xpath("//ul[contains(@class, 'ylist') and contains(@class,'ylist-bordered') and contains(@class, 'reviews')]/li")
    reviewDict = dict()
    for i in range(1, len(reviewlist)):
        reviews= reviewlist[i].xpath(".//p[@lang='en']/text()")
        stars= reviewlist[i].xpath("//div[contains(@title, int) and contains(@title, 'star rating')]")
        starText = stars[i].get('title')
        reviewDict[str(i)] = {"review":reviews, "starText":starText}

    wordDict = dict()   # Stores all words as dicitonary keys
    wordTotals = dict()
    for reviewInfo in reviewDict.keys():    # reviewInfo is a dicitionary key
        for review in range(len(reviewDict[reviewInfo]["review"])): # review is the index of the review in reviews (reviews is a list)
            for word in reviewDict[reviewInfo]["review"][review].translate(str.maketrans('', '', string.punctuation)).split(" "):  # Removes punctuation from all words and splits the review words by each whitespace
                try:    #If word has been seen
                    wordDict[word.lower()]
                except KeyError:    # else Make key dictionary for word
                    wordDict[word.lower()] = dict()
                try:
                    wordTotals[word.lower()]["fullCount"] += 1
                except KeyError:
                    wordTotals[word.lower()] = {"fullCount":1}           
                try:    #If word has been seen
                    wordDict[word.lower()][reviewInfo][review]["count"] += 1
                except KeyError:    # else make dict with count of one (since we have now seen it at least once).
                    wordDict[word.lower()][reviewInfo] = {review:{"count":1}}
        
    mostCommon = []
    limit = 10
    for word in wordDict.keys():
        if len(mostCommon) < limit:
            mostCommon.append(word)
            if len(mostCommon) == limit:
                mostCommon = sorted(mostCommon,key=lambda x:wordTotals[x]["fullCount"])
        elif len(mostCommon) == limit:
            for i in range(len(mostCommon)):
                if wordTotals[word]["fullCount"] > wordTotals[mostCommon[i]]["fullCount"]:
                    if i + 1 == len(mostCommon) or wordTotals[word]["fullCount"] <= wordTotals[mostCommon[i+1]]["fullCount"]:
                        mostCommon[i] = word

    pg = pygal.Bar()
    for word in mostCommon:
        pg.add(word,[wordTotals[word]["fullCount"]])
    pg.render_to_file("wordFreq.svg")