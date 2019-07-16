#!/usr/bin/env python
"""mapper.py"""

import sys

for line in sys.stdin:
    topn_tw = ['beat', 'friends', 'goals', 'kid', 'pro', 'embiid', 'face', 'hate', 'hey', 'lost', 'pretty']
    for word in topn_tw:
        if word in line:
            texts=line.strip().split()
            for text in texts:
                if text!=word:
                    print "%s|%s\t%s" % (word, text, 1)

