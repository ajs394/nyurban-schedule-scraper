import os

import numpy as np
from keras.layers import Activation, Dense
from keras.models import Sequential
from keras.utils import np_utils
from numpy import array
from sklearn.model_selection import train_test_split
from tinydb import TinyDB

from data.dnd_monster_dbo import data_point_from_record
from data.features import DETAILED, FEATURE_SET, MONSTER, NEITHER
from constants.data import db_name

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../data/{}.json'.format(db_name))
data_table = TinyDB(filename).table('data')

data = data_table.all()

inputs = []
outputs = []
for d in data:
    dp = data_point_from_record(d)
    i = []
    for f in FEATURE_SET:
        i += [dp.features[f]]
    inputs += [i]
    outputs += [DETAILED if dp.is_detailed else MONSTER if dp.is_monster else NEITHER]

X = array(inputs, dtype=object)
Y = array(outputs, dtype=object)
train_X, test_X, train_y, test_y = train_test_split(X, Y, train_size=0.5, test_size=0.5, random_state=0)

# Simple feed-forward architecture
model = Sequential()
model.add(Dense(units=15, input_shape=(len(FEATURE_SET),)))
model.add(Activation("sigmoid"))
model.add(Dense(units=30))
model.add(Activation("sigmoid"))
model.add(Dense(units=3))
model.add(Activation("softmax"))
 
# Optimize with SGD
model.compile(loss='categorical_crossentropy', 
              optimizer='adam', metrics=['accuracy'])
 
# Fit model in batches
model.fit(train_X, train_y, epochs=36, batch_size=1)
 
# Evaluate model
loss, accuracy = model.evaluate(test_X, test_y, verbose=0)
print("Accuracy = {:.2f}".format(accuracy))

filename = os.path.join(dirname, 'features_take_2_sequential_model.h5')
model.save(filename)
