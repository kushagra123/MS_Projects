#!/usr/bin/env python
"""mapper.py"""

import sys

for line in sys.stdin:
    topn_cc = ['win', 'game', 'say', 'league', 'play', 'get', 'season', 'score', 'go', 'club']
    for word in topn_cc:
        if word in line:
            texts=line.strip().split()
            for text in texts:
                if text!=word:
                    print "%s|%s\t%s" % (word, text, 1)

