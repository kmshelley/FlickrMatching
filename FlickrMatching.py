# # Flickr Photo Matching
__author__='Katherine'

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import requests
from StringIO import StringIO
from PIL import Image
import ConfigParser as config
from bs4 import BeautifulSoup

CONFIG = './flickr_config.ini'

#read in Flickr API variables
c = config.ConfigParser()
c.read(CONFIG)
key=c.get('Flickr','key')
secret=c.get('Flickr','secret')
url=c.get('Flickr','url')
endpoint=c.get('Flickr','endpoint')
tags=c.get('Flickr','tags')
user=c.get('Flickr','user')

def photo_walk(url,**kwargs):
    """Iterates through photos using the Flickr REST API"""
    
    """INPUT: flickr api URL and cURL request payload information"""
    """OUTPUT: JSON of photo data to search"""
    photos=[]
    kwargs.update({ 'page': 1 }) #make sure to start on page 1
    
    #access Flickr API
    results = requests.get(url,params=kwargs)
    
    if results.status_code!=200:
        print "Failed to access Flickr API!"
        return
    
    #iterate through the list of images returned by the search,
    #use beautiful soup to parse the html output
    #while results.status_code==200: #<-- USE THIS IN PRODUCTION!
    while kwargs['page']<3: #<-- only iterate through the first two pages for testing
        soup=BeautifulSoup(results.content,'html.parser')
        #append photo data attributes
        photos+=[photo.attrs for photo in soup.find_all('photo')]
        #search the next page
        kwargs['page']+=1
        results = requests.get(url,params=kwargs)
    return photos
        
#get a list of photo data based on search
photos=photo_walk(url,method=endpoint,api_key=key,user_id=user,tags=tags,per_page=15)
print len(photos)

PHOTO='https://farm%s.staticflickr.com/%s/%s_%s.jpg' % (photos[0]['farm'],
                                                        photos[0]['server'],
                                                        photos[0]['id'],
                                                        photos[0]['secret'])

r = requests.get(PHOTO)
i = Image.open(StringIO(r.content))
print i.format, i.size, i.mode
pix = np.array(i)
print pix.shape
plt.imshow(pix)
plt.show()



