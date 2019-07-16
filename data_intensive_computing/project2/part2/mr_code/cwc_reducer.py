#!/usr/bin/env python
"""reducer.py"""

from operator import itemgetter
import sys

current_word = None
current_count = 0
word = None
dict_pair = {}
for line in sys.stdin:
    line = line.strip()
    wordpair, count = line.split('\t', 1)
    try:
        count = int(count)
    except ValueError:
        continue
    if current_word == wordpair:
        current_count += count
    else:
        if current_word:
            print "%s\t%s" % (current_word, current_count)
        current_count = count
        current_word = wordpair
if current_word == wordpair:
    print "%s\t%s" % (current_word, current_count)
