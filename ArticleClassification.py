try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

from bs4 import BeautifulSoup

def getAllDoxyDonkeyPosts(url,links):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response)
    for a in soup.findAll('a'):
        try:
            url = a['href']
            title = a['title']
            if title == "Older Posts":
                print(title, url)
                links.append(url)
                getAllDoxyDonkeyPosts(url,links)
        except:
            title = ""
    return

blogUrl = "http://doxydonkey.blogspot.in"
links = []
getAllDoxyDonkeyPosts(blogUrl,links)

def getDoxyDonkeyText(testUrl):
    request = urllib2.Request(testUrl)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response)
    mydivs = soup.findAll("div", {"class":'post-body'})
    
    posts =[]
    for div in mydivs:
        posts+=map(lambda p:p.text.replace("?"," "), div.findAll("li"))
    return posts

doxyDonkeyPosts = []
for link in links:
    doxyDonkeyPosts+=getDoxyDonkeyText(link)
    
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_df=0.5,min_df=2,stop_words='english')
X = vectorizer.fit_transform(doxyDonkeyPosts)
X
print(X[0])

from sklearn.cluster import KMeans
km = KMeans(n_clusters = 3, init = 'k-means++', max_iter = 100, n_init = 1, verbose = True)
km.fit(X)

import numpy as np
np.unique(km.labels_, return_counts=True)

text = {}
for i,cluster in enumerate(km.labels_):
    oneDocument = doxyDonkeyPosts[i]
    if cluster not in text.keys():
        text[cluster] = oneDocument
    else:
        text[cluster] += oneDocument
        
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import nltk 

_stopwords = set(stopwords.words('english') + list(punctuation)+["million","billion","year","millions","billions","y/y","'s","''","``"])
keywords = {}
counts={}
for cluster in range(3):
    word_sent = word_tokenize(text[cluster].lower())
    word_sent=[word for word in word_sent if word not in _stopwords]
    freq = FreqDist(word_sent)
    keywords[cluster] = nlargest(100, freq, key=freq.get)
    counts[cluster]=freq
    
unique_keys={}
for cluster in range(3):   
    other_clusters=list(set(range(3))-set([cluster]))
    keys_other_clusters=set(keywords[other_clusters[0]]).union(set(keywords[other_clusters[1]]))
    unique=set(keywords[cluster])-keys_other_clusters
    unique_keys[cluster]=nlargest(10, unique, key=counts[cluster].get)
    
unique_keys

article = "Facebook Inc. has been giving advertisers an inflated metric for the average time users spent watching a video, a measurement that may have helped boost marketer spending on one of Facebook’s most popular ad products. The company, owner of the world’s largest social network, only counts a video as viewed if it has been seen for more than 3 seconds. The metric it gave advertisers for their average video view time incorporated only the people who had watched the video long enough to count as a view in the first place, inflating the metric because it didn’t count anyone who didn’t watch, or watched for a shorter time. Facebook’s stock fell more than 1.5 percent in extended trading after the miscalculation was earlier reported in the Wall Street Journal. Facebook had disclosed the mistake in a posting on its advertiser help center web page several weeks ago. Big advertising buyers and marketers are upset about the inflated metric, and asked the company for more details, according to the report in the Journal, citing unidentified people familiar with the situation. The Menlo Park, California-based company has kept revenue surging in part because of enthusiasm for its video ads, which advertisers compare in performance to those on Twitter, YouTube and around the web."

from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(n_neighbors=3)
classifier.fit(X,km.labels_)

test=vectorizer.transform([article])

test

prediction = classifier.predict(test)























