#! /home/hadoop/anaconda2/bin/python

# # Flickr Photo Matching Mapper
__author__='Katherine'
import os
import sys
import numpy as np
from scipy.spatial.distance import euclidean
import requests
import json
from StringIO import StringIO
from PIL import Image, ImageFilter
from os.path import expanduser


sys.path.append('.')
HOME = expanduser('~')

def normalize_photos(im1,im2,h=None,w=None):
    """
        Normalizes two PIL image objects by setting them to mode 'L' and setting the sizes equal
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

def compare_photos_MR(filename,photo):
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

    #load the file images
    im1 = Image.open(photo)
    im2=Image.open(filename)
        
    #get the image data from Flickr
    #photo = photo.lower().replace('https','http')
    #r = requests.get(photo)
    #im1 = Image.open(StringIO(r.content))

    transformations = [Image.FLIP_LEFT_RIGHT,
                       Image.FLIP_TOP_BOTTOM,
                       Image.ROTATE_90,
                       Image.ROTATE_180,
                       Image.ROTATE_270]
    
    #shrink both photos down to 100X100 pixels, convert to luminance values
    norm1,norm2 = normalize_photos(im1,im2,h=100,w=100)
    
    #if the images are already highly correlated return a line of text with the two image uri's
    if euclidean(norm1.flatten(),norm2.flatten()) <= min_dist:
        min_dist = euclidean(norm1.flatten(),norm2.flatten())
    #iterate through different transformations and compare correlation
    for t in transformations:
        new_img = np.array(Image.fromarray(norm2).transpose(t))#perform a transformation on the image
        if euclidean(norm1.flatten(),new_img.flatten()) <= min_dist:
            min_dist = euclidean(norm1.flatten(),new_img.flatten())
    return min_dist
     
if __name__=='__main__':
    #compare photos pair-wise
    for line in sys.stdin:
        data = line.strip().split('\t')
        if len(data)==2:
            f,g = data
            filename = 'modified.jar/' + f
            photo = 'originals.jar/' + ('.').join(g.replace('https://static.flickr.com/','').split('/'))
            #full_f = './images/modified_images/%s' % f
            try:
                dist = compare_photos_MR(filename,photo)
                sys.stdout.write('%s\t%s|%s\n' % (f,g,str(dist)))
            except Exception as e:
                sys.stdout.write('ERROR: ' + str(e) + '\n')
        
