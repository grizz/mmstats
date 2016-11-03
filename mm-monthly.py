#!/usr/bin/env python
from __future__ import print_function

from collections import Counter
from contextlib import contextmanager
import gzip
import os
import re
import sys


def parse_post(fobj, month):
    rv = {}
    regex = re.compile('^%s \d\d \d\d:\d\d:\d\d \d{4} \(\d+\) post to (?P<listname>[^ ]+) from (?P<poster>.+?), .*' % (month,))

    for line in fobj:
        m = regex.match(line)
        if m:
            rv.setdefault(m.group('listname'), Counter())[m.group('poster')] += 1
#            rv[m.group('listname')] += 1
            print("POSTER " + m.group('poster'))

    print(rv)
    return rv


def parse_vette(fobj, month):
    rv = Counter()
    regex = re.compile('^%s \d\d \d\d:\d\d:\d\d \d{4} \(\d+\) (?P<listname>[^:]+): .*' % (month,))

    for line in fobj:
        m = regex.match(line)
        if m:
            rv[m.group('listname')] += 1

    return rv


@contextmanager
def fopen(fname):
    try:
        if fname.endswith('.gz'):
            fobj = gzip.open(fname)
        else:
            fobj = open(fname)

        yield fobj

    finally:
        fobj.close()


def main(log_dir, month):
    posted = {}
    moderated = Counter()

    for fname in os.listdir(log_dir):
        fq_name = os.path.join(log_dir, fname)

        if fname.startswith('post'):
            print(fname)
            with fopen(fq_name) as fobj:
                parsed = parse_post(fobj, month)
                for k, v in parsed.items():
                    if k in posted:
                        posted[k] += v
                    else:
                        posted[k] = v

        elif fname.startswith('vette'):
            print(fname)
            with fopen(fq_name) as fobj:
                moderated += parse_vette(fobj, month)

    print("## Statistics for {}".format(month))
    print()
    print("### Posts by list")
    for k, v in posted.items():
        print("#### " + k)
        print("post count {}".format(sum(v.values())))
        print("unique posters {}".format(len(v)))
        print()
    print()
    print("### Moderated by list")
    print('\n'.join(["{0}: {1}".format(k, v) for k, v in moderated.items()]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: {} <logdir> <month>'.format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
