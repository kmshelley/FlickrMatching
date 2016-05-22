## Flickr Photo Matching

Katherine Shelley

## How to Run

To run FlickrMatching, clone this repo and run `pip install requirements.txt` to download the dependencies. This code depends on a number of Python libraries such as numpy, scipy, matplotlib, PIL, and flickrapi.

Enter your Flickr API key, secret key, a Flickr username, and photo tags to search in `flickr_config.ini`.

Finally, run the code with:

```python FlickrMatching.py```


## Data Collection

For collecting the image data from Flickr I first utilized the Python **requests** library to perform iterative cURL requests to the photo search API endpoint. This script had issues with paging, so I later switched to the Python Flickr API, **flickrapi**.

Image location data is collected using the def `photo_walk` that pages through API photo search results and returns a JSON object of API photo results. The data output by the Flickr API search helps build the exact URLs for accessing each image.

## Photo Comparison

The def `compare_photos` is used to identify the original images. For each modified image, we call `compare_photos` which takes as input a modified image filename, and the output data list that identifies the original image Flickr URLs. `compare_photos` starts by setting a minimum distance measure to positive infinity and a "best pick" for the original image to be Null. The function iterates through the search results from Flickr, loads the modified image and a potential original as Python Image Library (PIL) image objects, and the photos are normalized by setting their sizes to the minimum height and width of the pair. They are also converted from RGB to Luminence values and converted to Numpy arrays.

After normalization the two images are compared for similarity by using a basic euclidean distance measure. For each potential original image the distance is measured, if the pair of images have the smallest distance measured thus-far, the current potential original image is classified as the "best pick" in the iteration and the current distance is set as the new minimum observed distance. In addition to comparing the normalized images, the modified image is also sent through a list of transformations; flipped left-to-right, flipped top-to-bottom, rotated 90, 180, and 270 degrees. Each transformed normalized image is also compared to the potential original for distance. This is done as a means of reducing the distance between an image that has been modified and its original, and (hopefully) increasing the distance between different but similar images.

The surviving "best pick" photo at the end of the iteration is the best choice for the original image. The function then outputs a string  of '*modified filename*,*flickr original url*\n' for writing results to disk.

## Future Steps and Considerations

The current iterative method of comparing the modified photos is not at all efficient.

First, the current method accesses the original images by iterating through the Flickr URL's given by the `photo_walk` output for each modified image. I originally made the decision to do this because I wanted to make sure the code would scale, i.e. I did not want to rely on storing the original images locally. However, accessing the same image 1700-plus times is not efficient.

Second, the current method of comparing images performs a brute-force image-to-image comparison which also does not scale.

I believe both of these issues could be alleviated with a better algorithm built for comparing the similarity of two large sets, such as minhashing. An initial thought would be to load all the original and modified images as numpy arrays in memory, then perform a set-to-set comparison using a more efficient data-mining algorithm.

Unfortunately, in two hours I did not have the time to test out such an implementation.
