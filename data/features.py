
DETAILED = [1, 0, 0]
MONSTER = [0, 1, 0]
NEITHER = [0, 0, 1]

MONSTER_STAT_KEYWORDS = [
    #"Challenge",
    "CR",
    "Hit Dice",
    "Hit Points", 
    #"HP",
    "Armor Class", 
    "AC",
    #"dungeon",
    "dragon"
]

MONSTER_FULL_STAT_KEYWORDS = [
    "Actions",
    "Languages",
    "Saving",
    #"Throws",
    #"Skills",
    "STR",
    #"DEX",
    "Speed",
    #"alignment"
]

WORD_COUNT_FEATURES = list(set(MONSTER_STAT_KEYWORDS) | set(MONSTER_FULL_STAT_KEYWORDS))

# search in visible text:
# word counts
# page length
# number of unique words

PAGE_LENGTH = "PAGE_LENGTH"
NUM_UNIQUE = "NUM_UNIQUE"
_OTHER_FEATURES = [
    PAGE_LENGTH,
    NUM_UNIQUE
]

URL_CHARACTER_COUNTS = [
    #'.',
    #'-',
    '?',
    #'!',
    #'/',
    '=',
    #'#'
]

FEATURE_SET = list(set(WORD_COUNT_FEATURES) | set(_OTHER_FEATURES) | set(URL_CHARACTER_COUNTS))
FEATURE_SET.sort()