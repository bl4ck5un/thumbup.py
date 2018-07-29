#!/usr/bin/env python


import argparse
import logging
import multiprocessing
import sys

import Job
import Processor

version = '1.3.0'
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger('main')

def main():
    """The main function of thumbup.
    """
    parser = argparse.ArgumentParser(description="thumbup video thumbnail generator v%s" % version)
    parser.add_argument('input', metavar='FILE', nargs='+',
                        help='one or more video files or directories (with -r)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='logging more stuff')
    parser.add_argument('-r', '--rec', dest='recur', action='store_true', default=False,
                        help='recursively go into all dirs')
    parser.add_argument('-f', '--force', dest='overwrite', action='store_true', default=False,
                        help='force overwrite existing thumbnails')
    parser.add_argument('-o', '--offset', dest='offset', metavar='OFFSET', type=str, default="60",
                        help='skip OFFSET (hh:mm:ss.ms or second) from the beginning')
    parser.add_argument('-s', '--suffix', dest='suffix', metavar='X', type=str, default="",
                        help="add suffix to the output filename, input.mp4 -> inputX.jpg")

    options = parser.parse_args()

    if options.verbose:
        logger.setLevel(logging.DEBUG)

    jobs = []

    try:
        for filename in options.input:
            jobs += Job.dir_scanner(filename, options)
    except Exception as e:
        print 'Cannot parse input', str(e)
        sys.exit(-1)

    logger.info('collected %d jobs' % len(jobs))

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    procs = [Processor.Processor(j, pool, options) for j in jobs]

    for idx, p in enumerate(procs):
        logging.info('[%d / %d]' % (idx, len(procs)))
        p.run_noexcept()

    logger.info('Done.')


if __name__ == '__main__':
    main()
