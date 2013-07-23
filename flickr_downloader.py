#!/usr/bin/python

import urllib
import urllib2
import json
import sys
import os

from workqueue import WorkQueue

FLICKR_API_URL = "http://api.flickr.com/services/rest"
FLICKR_API_KEY = "ad7b7b6be35e8a6acbca6eb897c6dc63"

FLICKR_GETINFO_REQUEST = "flickr.photosets.getInfo"
FLICKR_LIST_REQUEST = "flickr.photosets.getPhotos"
FLICKR_GETSIZES_REQUEST = "flickr.photos.getSizes"
PHOTOS_PER_PAGE = 500

num_downloaded = 0
num_photos = 0

def createApiRequest(method, args = None):
	args["method"] = method
	args["api_key"] = FLICKR_API_KEY
	args["format"] = "json"
	args["nojsoncallback"] = "1"

	return urllib2.Request(FLICKR_API_URL, urllib.urlencode(args))
	
def usage():
	print sys.argv[0] + " <photo_set_id> <target directory>"
	sys.exit(1)

def downloadPhoto(photo_md):
	global num_downloaded

	filename = photo_dir + "/img_" + photo_md['id'] + ".jpg"
	if (not os.path.exists(filename)):
		request = createApiRequest(FLICKR_GETSIZES_REQUEST, {'photo_id':photo_md['id']})
		handler = urllib2.urlopen(request)
		size_response = json.loads(handler.read())

		for size_md in size_response['sizes']['size']:
			if size_md['label'] == 'Original':
				request = urllib2.Request(size_md['source']);
				handler = urllib2.urlopen(request)
				f = open(filename + ".part", "w")
				f.write(handler.read())
				f.close()
				os.rename(filename + ".part", filename)
		
	num_downloaded += 1
	print "Downloaded " + str(num_downloaded) + "/" + str(num_photos)


if len(sys.argv) != 3:
	usage();

photo_set_id = sys.argv[1]
target_dir = sys.argv[2]

request = createApiRequest(FLICKR_GETINFO_REQUEST, {'photoset_id':photo_set_id})

handler = urllib2.urlopen(request)  
response = json.loads(handler.read())

album_name = response['photoset']['title']['_content']
num_photos = int(response['photoset']['photos'])
photo_dir = target_dir + "/" + album_name

try:
	os.mkdir(photo_dir)
except OSError:
	res = raw_input(photo_dir + " exists! Continue? (y/n) ")

	if (res == "y"):
		pass
	else:
		raise

print "Downloading " + str(num_photos) + " photos from album " + album_name

num_pages = num_photos / PHOTOS_PER_PAGE + 1
page = 1
wq = WorkQueue(downloadPhoto)

while True:
	request = createApiRequest(FLICKR_LIST_REQUEST, {'photoset_id':photo_set_id, 'page':page})

	handler = urllib2.urlopen(request)  
	response = json.loads(handler.read())

	for photo_md in response['photoset']['photo']:
		wq.add(photo_md)
	
	page += 1
	num_pages = response['photoset']['pages']

	if page > num_pages:
		break

wq.done()
print "Done!"
