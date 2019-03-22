import os
import sys

from keras.models import load_model
from numpy import array
from numpy.linalg import norm

from data.dnd_monster_dbo import data_point
from data.features import DETAILED, FEATURE_SET, MONSTER, NEITHER

classifier = None
prediction_helpers = [
    ("Monster", lambda a: get_distance_of_lists(a, MONSTER)),
    ("Detailed", lambda a: get_distance_of_lists(a, DETAILED)),
    ("Neither", lambda a: get_distance_of_lists(a, NEITHER))
]

def get_distance_of_lists(a, b):
    return norm(array(a)-array(b))

def get_classifier():
    global classifier
    if classifier == None:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../model/features_take_2_sequential_model.h5')
        classifier = load_model(filename)
    return classifier

def classify_page(page: data_point):
    features = page.features
    
    inputs = []
    
    i = []
    for f in FEATURE_SET:
        i += [features[f]]
    inputs += [i]

    X = array(inputs, dtype=object)
    prediction = get_classifier().predict(X)

    return get_closest_prediction(prediction)

def get_closest_prediction(prediction):
    min = sys.maxsize
    pred = ""
    for helper in prediction_helpers:
        curr = helper[1](prediction)
        if curr < min:
            pred = helper[0]
            min = curr
    return pred
    
