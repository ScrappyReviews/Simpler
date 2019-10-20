import requests
from lxml import html
import string
import pygal
from textblob import TextBlob
from pygal.style import Style

def wordCon(webTitle, graphFileName, wordTotals = [dict()]):
    positiveWords = [] 
    negativeWords = []
    for word in wordTotals.keys():
        w3 = TextBlob(word).sentiment.polarity
        if w3 > 0.5:
            positiveWords.append(word)
        elif w3 < -0.5:
            negativeWords.append(word)
    
    style = Style(font_family='googlefont:Raleway', label_font_size = 18, title_font_size = 18)
    pg = pygal.StackedBar(style=style)
    pg.x_labels = 'Positive Words', 'Negative Words'
    pg.title = webTitle
    for word in positiveWords:
        pg.add(word, [wordTotals[word]["fullCount"], None])
    for word in negativeWords:
        pg.add(word, [None, wordTotals[word]["fullCount"]])
    pg.render_to_file(graphFileName)

def getYelpReviewInfo(link="https://www.yelp.com/biz/bueno-y-sano-amherst"):
    link = link.strip()
    response = requests.get(link)
    root = html.fromstring(response.content)
    pageid = root.xpath("//div[@class='lemon--div__373c0__1mboc border-color--default__373c0__2oFDT']")[0]
    reviewlist = pageid.xpath("//ul[contains(@class, 'lemon--ul__373c0__1_cxs') and contains(@class, 'undefined') and contains(@class, 'list__373c0__2G8oH')]/li")
    reviewDict = dict()
    for i in range(1, len(reviewlist)):
        reviews= reviewlist[i].xpath(".//span[@class='lemon--span__373c0__3997G']/text()")
        if len(reviews) > 0:
            reviewDict[str(i)] = {"review":reviews}

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
    webTitle = root.xpath("//meta[@property = 'og:title']")[0].attrib["content"]
    graphFileName = "{}.svg".format(link.split("/")[-1])
    wordCon(webTitle, graphFileName, wordTotals)
    return graphFileName

def getRestaurants(location="Amherst+MA"):
    queryLink = "https://www.yelp.com/search?find_desc=&find_loc={}".format(location)
    queryResponse = requests.get(queryLink)
    root = html.fromstring(queryResponse.content)
    restaurantContainer = root.xpath("//ul[contains(@class,'lemon--ul__373c0__1_cxs') and contains(@class,'undefined') and contains(@class,'list__373c0__2G8oH')]")
    restaurantList = []    
    for i in range(len(restaurantContainer)):
        search = restaurantContainer[i].xpath("//a[contains(@class,'lemon--a__373c0__IEZFH') and contains(@class,'link__373c0__29943') and contains(@class,'photo-box-link__373c0__1AvT5') and contains(@class,'link-color--blue-dark__373c0__1mhJo') and contains(@class,'link-size--default__373c0__1skgq')]")
        if len(search) > 0:
            for item in search:
                if "biz" in item.attrib["href"][:5]:
                    print(item.attrib["href"])
                    restaurantList.append(item.attrib["href"])
    restaurantSet = set(restaurantList)
    restaurantList = [link for link in restaurantSet]
    graphNameList = []
    for link in restaurantList:
        graphNameList.append(getYelpReviewInfo("https://www.yelp.com{}".format(link)))
    return graphNameList
