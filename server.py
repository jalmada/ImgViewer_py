from flask import Flask, jsonify, render_template, Response, request, stream_with_context, send_file
from flask_cors import CORS
from urllib.request import urlopen, urlretrieve
import csv
from cachelib import SimpleCache
import os.path
import shutil
import os



cacheFile = SimpleCache()
cacheImages = SimpleCache()
app = Flask(__name__, template_folder='public')
CORS(app)

imagescsvUrl = 'https://pastebin.com/raw/BmA8B0tY'
images = {}
imagesDir = 'public/images'
@app.route('/')
def index():
    return render_template('index.html') 


@app.route('/image', methods=['GET'])
def image():
    isGrayscale = request.args.get('grayscale') is not None
    id = request.args.get('id')
    return send_file(getImageLocalUrl(id, isGrayscale), mimetype='image/jpg')


def getImageLocalUrl(imgId, isGrayscale):
    return downloadImage(imgId, isGrayscale)



def getImagesData():
    images = cacheFile.get('images')

    if images is None:
        images = {};
        if os.path.isdir(imagesDir):
            shutil.rmtree(imagesDir)
        
        os.mkdir(imagesDir)
        urlretrieve(imagescsvUrl, 'images.csv')
        with open('images.csv') as csvfile:
            reader = csv.reader(csvfile)
            
            for i in reader:
                id = i[0].split('/')[4]
                images[id] = i[0]

            cacheFile.set('images', images, timeout=5 * 60)
    return images

def downloadImage(id, isGrayscale):

    imgUrl = getImagesData()[id]
    imgUrl += '?grayscale' if isGrayscale else ''
    gray = '_gray' if isGrayscale else ''
    imgLocal = ''

    #check cache
    imgLocal = cacheImages.get(id)
    if imgLocal is None or not os.path.isfile(imgLocal):
        print('cacheEx')
        imgLocal = f'{imagesDir}/{id}{gray}.jpg'
        urlretrieve(imgUrl, imgLocal)
        cacheImages.set(id, imgLocal, timeout= 1 * 60)
    
    return imgLocal

if (__name__ == '__main__'):
    images = getImagesData()
    app.run(host='0.0.0.0', port=3000,  threaded=True)