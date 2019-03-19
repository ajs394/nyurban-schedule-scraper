from keras.layers import Activation, Dense
from keras.models import Sequential
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from tinydb import TinyDB
from numpy import array
import numpy as np

from dnd_monster_dbo import data_point_from_record
from process_potential_dnd_page import FEATURE_SET

DETAILED = [1, 0, 0]
MONSTER = [0, 1, 0]
NEITHER = [0, 0, 1]

data_table = TinyDB('data/monsters.json').table('data')

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
model.add(Dense(16, input_shape=(len(FEATURE_SET),)))
model.add(Activation("sigmoid"))
model.add(Dense(units=3))
model.add(Activation("softmax"))
 
# Optimize with SGD
model.compile(loss='categorical_crossentropy', 
              optimizer='adam', metrics=['accuracy'])
 
# Fit model in batches
model.fit(train_X, train_y, epochs=100, batch_size=1)
 
# Evaluate model
loss, accuracy = model.evaluate(test_X, test_y, verbose=0)
print("Accuracy = {:.2f}".format(accuracy))

model.save('model/monster_page_sequential_model.h5')