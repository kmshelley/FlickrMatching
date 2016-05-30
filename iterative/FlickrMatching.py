# # Flickr Photo Matching
__author__='Katherine'
import os
import numpy as np
from scipy.spatial.distance import euclidean
import requests
import flickrapi
import json
from StringIO import StringIO
from PIL import Image, ImageFilter
import ConfigParser as config
import datetime as dt

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

def normalize_photos(im1,im2,h=None,w=None):
    """
        Normalizes to PIL image objects by setting them to mode 'L' and setting the sizes equal
        INPUT: two PIL image objects, OPTIONAL height and width to resize the images
        OUTPUT: normalized images as numpy arrays
    """
    h1,w1=im1.size
    h2,w2=im2.size

    #if a height and width are not given, use the min height and width of the photos
    if not h and w: h,w = min(h1,h2),min(w1,w2)
    adj1 = np.array(im1.resize((h,w)).convert('L'))
    adj2 = np.array(im2.resize((h,w)).convert('L'))
    
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

    
def compare_photos_simple(filename,photos):
    """
        Compares a modified image to a flickr API result
        INPUT: File name of a modified image, dict of flickr API search result
        OUTPUT: True if the two images are the same, false if not

        Uses simple normalization: sets photos to be the same size, and grayscale
    """
    f = os.path.basename(filename)
    #define the results csv line as the base file name and the flickr static url
    min_dist=float('inf')
    best_pick=None

    #load the file image
    im2=Image.open(filename)
    for p in photos:
        PHOTO='https://static.flickr.com/%s/%s_%s.jpg' % (p['server'],p['id'],p['secret'])

        
        #get the image data from Flickr
        r = requests.get(PHOTO)
        im1 = Image.open(StringIO(r.content))
        
        
        #shrink both photos down to 100X100 pixels, convert to luminance values
        norm1,norm2 = normalize_photos(im1,im2,h=100,w=100)
        
        #if the images are already highly correlated return a line of text with the two image uri's
        if euclidean(norm1.flatten(),norm2.flatten()) <= min_dist:
            best_pick=PHOTO
            min_dist = euclidean(norm1.flatten(),norm2.flatten())
    return f+','+best_pick+'\n'
        


def compare_photos(filename,photos):
    """
        Compares a modified image to a flickr API result
        INPUT: File name of a modified image, dict of flickr API search result
        OUTPUT: True if the two images are the same, false if not

        Uses simple normalization: sets photos to be the same size, and grayscale
    """
    f = os.path.basename(filename)
    #define the results csv line as the base file name and the flickr static url
    min_dist=float('inf')
    best_pick=None

    #load the file image
    im2=Image.open(filename)
        
    for p in photos:
        PHOTO='https://static.flickr.com/%s/%s_%s.jpg' % (p['server'],p['id'],p['secret'])
        #get the image data from Flickr
        r = requests.get(PHOTO)
        im1 = Image.open(StringIO(r.content))
        

        transformations = [Image.FLIP_LEFT_RIGHT,
                           Image.FLIP_TOP_BOTTOM,
                           Image.ROTATE_90,
                           Image.ROTATE_180,
                           Image.ROTATE_270]
        
        #shrink both photos down to 100X100 pixels, convert to luminance values
        norm1,norm2 = normalize_photos(im1,im2,h=100,w=100)
        
        #if the images are already highly correlated return a line of text with the two image uri's
        if euclidean(norm1.flatten(),norm2.flatten()) <= min_dist:
            best_pick=PHOTO
            min_dist = euclidean(norm1.flatten(),norm2.flatten())
        #iterate through different transformations and compare correlation
        for t in transformations:
            new_img = np.array(Image.fromarray(norm2).transpose(t))#perform a transformation on the image
            if euclidean(norm1.flatten(),new_img.flatten()) <= min_dist:
                best_pick=PHOTO
                min_dist = euclidean(norm1.flatten(),new_img.flatten())
    return f+','+best_pick+'\n'
     
if __name__=='__main__':
    #get a list of photo data based on search
    start=dt.datetime.now()
    flickr = flickrapi.FlickrAPI(key, secret, format='json')
    
    photos = photo_walk(flickr,user_id=user,tags=tags,per_page=500)
    print "%d images collected. Collection runtime: %s" % (len(photos),str(dt.datetime.now()-start))

    #write results to disk
    ##These list-comprehensive runs were taking too long. Write iteratively to get at least *SOME* results
    #results =[compare_photos(os.path.join(MODIFIED,filename),photos) for filename in os.listdir(MODIFIED)]
    for filename in os.listdir(MODIFIED): 
        with open('results.csv','a') as out:
            out.write(compare_photos(os.path.join(MODIFIED,filename),photos))
    print "Done comparing images. Total runtime: %s" % str(dt.datetime.now()-start)

    
    
