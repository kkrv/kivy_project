import os
import time

import cv2
import io
import numpy as np
from tinydb import TinyDB, Query
from style_transfer.style_transfer import get_stylized_image
from flask import Flask, jsonify, request

app = Flask(__name__)
model = None
filters = ['mosaic', 'wave']
cur_filter_id = 0
applied = False
db = TinyDB('db/db.json')
path_to_img = 'db/imgs'


@app.route('/transfer/<filter_id>', methods=['POST'])
def transfer(filter_id):
    img = request.files['image']
    image_stream = io.BytesIO()
    image_stream.write(img.read())
    image_stream.seek(0)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    style_weights = os.path.join(os.path.join('style_transfer', 'weights'), filters[int(filter_id)] + '.hdf5')
    gen_img = get_stylized_image(img, style_weights)

    global db
    global path_to_img
    timestr = time.strftime("%Y%m%d_%H%M%S")
    im_path = "IMG_{}.png".format(timestr)
    path = os.path.join(path_to_img, im_path)
    cv2.imwrite(path, gen_img)
    db.insert({'style': int(filter_id), 'img': path})

    _, img_encoded = cv2.imencode('.jpg', gen_img)
    return jsonify({'res_img': img_encoded.tostring().hex(),
                    'result': 'OK'}), 201


if __name__ == "__main__":
    app.run()
