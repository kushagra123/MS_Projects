#!/usr/bin/env python
"""mapper.py"""

import sys

for line in sys.stdin:
    topn_nyt = ['say', 'team', 'game', 'one', 'league', 'mr', 'time', 'play', 'last', 'would']
    for word in topn_nyt:
        if word in line:
            texts=line.strip().split()
            for text in texts:
                if text!=word:
                    print "%s|%s\t%s" % (word, text, 1)

