#!/usr/bin/env python


import Job
import Processor

import logging
import sys
import multiprocessing
from optparse import OptionParser

import argparse

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger('main')


def main():
    """The main function of thumbup.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='FILE', nargs='+',
                        help='one or more video files or directories (with -R)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='logging more stuff')
    parser.add_argument('-r', '--rec', dest='recur', action='store_true', default=False,
                        help='recursively go into all dirs')
    parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true', default=False,
                        help='overwrite existing thumbnails')
    parser.add_argument('--offset', dest='offset', metavar='OFFSET', type=int, default=60,
                        help='skip OFFSET (sec) from the beginning')

    options = parser.parse_args()

    jobs = []

    try:
        for filename in options.input:
            jobs += Job.dir_scanner(filename, options)
    except:
        print 'Cannot parse input'
        sys.exit(-1)

    logger.info('collected %d jobs' % len(jobs))

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    procs = [Processor.Processor(j, pool, options) for j in jobs]

    for idx, p in enumerate(procs):
        print '[%d / %d]' % (idx, len(procs))
        p.run_noexcept()

    logger.info('Done.')


if __name__ == '__main__':
    main()
