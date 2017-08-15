#!/usr/bin/env python

import sys
import os
from optparse import OptionParser

import Processor


#---------------- main ------------------#
optparser = OptionParser()
optparser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
optparser.add_option("-R", action="store_true", dest="recur", default=False)
optparser.add_option("-O", "--overwrite", action="store_true", dest="overwrite", default=False)


def run(filename):
    # recursion to inner dir
    ext = os.path.splitext(filename)[1]
    if not os.path.isdir(filename) and \
        ext.lower() not in ('.m4v', '.wmv', '.avi', '.mkv', '.mp4', '.vob'):
        return

    if os.path.isdir(filename):
        if options.recur:
            if options.verbose:
                print 'REC enter %s' % filename
            for f in os.listdir(filename):
                ff = os.path.join(filename, f)
                run(ff)
            if options.verbose:
                print 'REC leave %s' % filename
        else:
            print '%s is a directory' % filename
        return 0

    proc = Processor.Processor(filename, overwrite=options.overwrite)
    proc.run()

try:
    (options, args) = optparser.parse_args()
except:
    print 'Usage: python thumbgen.py file1 file2'
    sys.exit(-1)

try:
    if args:
        for filename in args:
            run(filename)
    else:
        while True:
            filename = raw_input('Filename: ')
            run(filename)
except (EOFError, KeyboardInterrupt):
    os.sys.stdout.write('Done.\n')
