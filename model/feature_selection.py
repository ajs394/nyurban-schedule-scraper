import os

from numpy import array
from sklearn.feature_selection import SelectKBest, chi2
from tinydb import TinyDB

from constants.data import db_name
from data.dnd_monster_dbo import data_point_from_record
from data.features import DETAILED, FEATURE_SET, MONSTER, NEITHER

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
    outputs += ['DETAILED' if dp.is_detailed else 'MONSTER' if dp.is_monster else 'NEITHER']

X = array(inputs, dtype=object)
Y = array(outputs, dtype=object)

#We will select the features using chi square

test = SelectKBest(score_func=chi2, k=10)

#Fit the function for ranking the features by score

fit = test.fit(X, Y)

#Summarize scores numpy.set_printoptions(precision=3) print(fit.scores_)

#Apply the transformation on to dataset

features = fit.transform(X)

feats = {}
count = 0

for score in fit.scores_:
    feats[count] = score
    count += 1
feats_by_value = sorted(feats.items(), key=lambda kv: kv[1], reverse=True)

for key, value in feats_by_value:
    print('{},{}'.format(FEATURE_SET[key], value))
