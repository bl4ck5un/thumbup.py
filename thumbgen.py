#!/usr/bin/env python

import sys
import os
import Job
from optparse import OptionParser

import multiprocessing
import Processor


optparser = OptionParser()
optparser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
optparser.add_option("-R", action="store_true", dest="recur", default=False)
optparser.add_option("-O", "--overwrite", action="store_true", dest="overwrite", default=False)
optparser.add_option("--offset", action="store", dest="offset", type="int", default=60, metavar="OFFSET")


try:
    (options, args) = optparser.parse_args()
    assert args
except:
    print 'Usage: python thumbgen.py file1 file2'
    sys.exit(-1)

jobs = []

try:
    for filename in args:
        jobs += Job.dir_scanner(filename, options)
except:
    print 'Cannot parse input'
    sys.exit(-1)

count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes=count)

for j in jobs:
    try:
        Processor.Processor(j, pool, options).run()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        continue

print('Done.')
