import numpy as np
import tensorflow as tf
import cv2
import os

from style_transfer.model import build_model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def preprocess_img(img, target_shape=None):
    # image = cv2.imread(str(path))
    if target_shape is not None:
        img = cv2.resize(img, target_shape)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img = np.expand_dims(img, axis=0)
    return img


def get_stylized_image(content, style_weights):
    tf.reset_default_graph()
    transformation_model = build_model(input_shape=(None, None, 3))
    transformation_model.load_weights(style_weights)
    content_image = preprocess_img(content)
    gen = transformation_model.predict(content_image)

    gen = np.squeeze(gen)
    gen = gen.astype(np.uint8)
    gen = cv2.cvtColor(gen, cv2.COLOR_RGB2BGR)
    tf.keras.backend.clear_session()

    return gen
