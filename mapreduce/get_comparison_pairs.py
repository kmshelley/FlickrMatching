# # Flickr Photo Matching
__author__='Katherine'
import os
import requests
import flickrapi
import ConfigParser as config
from itertools import product
import datetime as dt
import json

CONFIG = '../flickr_config.ini'
MODIFIED = '../modified_images/'
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

     
if __name__=='__main__':
    #get a list of photo data based on search
    start=dt.datetime.now()
    flickr = flickrapi.FlickrAPI(key, secret, format='json')
    
    photos = photo_walk(flickr,user_id=user,tags=tags,per_page=500)
    print "%d images collected. Collection runtime: %s" % (len(photos),str(dt.datetime.now()-start))

    #write pairs of photos to compare to txt file
    with open('./to_process.txt','w') as out:
        [out.write('%s\thttp://static.flickr.com/%s/%s_%s.jpg\n' % (f,p['server'],p['id'],p['secret'])) for f,p in product(os.listdir(MODIFIED),photos) if f.split('.')[-1]=='png']
        
    print "Done gathering comparison pairs. Total runtime: %s" % str(dt.datetime.now()-start)

    
    
