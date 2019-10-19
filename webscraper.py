import requests
from lxml import html

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
