# # Flickr Photo Matching
__author__='Katherine'
import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import requests
import flickrapi
import json
from StringIO import StringIO
from PIL import Image
import ConfigParser as config
from bs4 import BeautifulSoup
from itertools import product
import datetime as dt

CONFIG = './flickr_config.ini'
MODIFIED = './modified_images/'
BASEURL = 'http://static.flickr.com/'

#read in Flickr API variables
c = config.ConfigParser()
c.read(CONFIG)
key=c.get('Flickr','key')
secret=c.get('Flickr','secret')
url=c.get('Flickr','url')
endpoint=c.get('Flickr','endpoint')
tags=c.get('Flickr','tags')
user=c.get('Flickr','user')



def BAD__photo_walk(url,**kwargs):
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
    #while True: #<-- for production
    while kwargs['page']<=50: #<-- for testing
        try:
            soup=BeautifulSoup(results.content,'html.parser')
            #append photo data attributes
            photos+=[photo.attrs for photo in soup.find_all('photo')]
            #search the next page
            kwargs['page']+=1
            results = requests.get(url,params=kwargs)
        except:
            break
    return photos

def photo_walk(flickr,**kwargs):
    """Iterates through photos using the Flickr REST API"""
    
    """INPUT: flickr api and search keywords"""
    """OUTPUT: JSON of photo data to search"""
    photos=[]
    kwargs.update({ 'page': 1 }) #make sure to start on page 1
    
    #access Flickr API
    #add first set of photo data to photos list
    results = json.loads(flickr.photos.search(**kwargs))['photos']
    photos+=results['photo']
    #iterate through the pages of images returned by the search,
    while kwargs['page'] < results['pages']: 
        try:
            #search the next page
            kwargs['page']+=1
            results = json.loads(flickr.photos.search(**kwargs))['photos']
            photos+=results['photo']
        except Exception as e:
            print e
            break
    return photos

def normalize_photos(im1,im2):
    """
        Normalizes to PIL image objects by setting them to mode 'L' and setting the sizes equal
        INPUT: two PIL image objects
        OUTPUT: normalized images as numpy arrays
    """
    h1,w1=im1.size
    h2,w2=im2.size
    
    max_h,max_w = max(h1,h2),max(w1,w2)
    adj1 = np.array(im1.resize((max_h,max_w)).convert('L'))
    adj2 = np.array(im2.resize((max_h,max_w)).convert('L'))
    
    return adj1,adj2

def image_correlation(im1,im2):
    """
        Measures the correlation between two images
        INPUT: Two images as numpy arrays
        OUTPUT: Cross-correlation between the matrices

        Correlation greater than 50 will be deemed the same image
    """
    
    arr1,arr2=im1.flatten(),im2.flatten() #flatten matrices into 1-D arrays
    
    return np.correlate(arr1,arr2).item()


def compare_photos(filename,photo):
    """
        Compares a modified image to a flickr API result
        INPUT: File name of a modified image, dict of flickr API search result
        OUTPUT: True if the two images are the same, false if not

        Uses simple normalization: sets photos to be the same size, and grayscale
    """
    f = os.path.basename(filename)
    #define the results csv line as the base file name and the flickr static url
    
    
    PHOTO='https://farm%s.staticflickr.com/%s/%s_%s.jpg' % (photo['farm'],
                                                            photo['server'],
                                                            photo['id'],
                                                            photo['secret'])

    
    #get the image data from Flickr
    r = requests.get(PHOTO)
    im1 = Image.open(StringIO(r.content))
    #load the file image
    im2=Image.open(filename)

    #if the images are highly correlated return a line of text with the two image uri's
    if image_correlation(*normalize_photos(im1,im2)) >= 40:
        return f+','+PHOTO
    
    
    
    
if __name__=='__main__':
    #get a list of photo data based on search (test with 1000 images)
    start=dt.datetime.now()
    flickr = flickrapi.FlickrAPI(key, secret, format='json')
    
    photos = photo_walk(flickr,user_id=user,tags=tags,per_page=500)
    print "%d images collected. Collection runtime: %s" % (len(photos),str(dt.datetime.now()-start))

    results = [compare_photos(os.path.join(MODIFIED,filename),photo) for filename,photo in product(os.listdir(MODIFIED),photos)]
    with open('results.csv','w') as out:
        out.writelines(results)
    print "Done writing comparing images. Total runtime: %s" % str(dt.datetime.now()-start)

    
    
