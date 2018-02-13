import os
import logging

logger = logging.getLogger(__name__)

SUPPORTED_EXT = ('.m4v', '.wmv', '.avi', '.mkv', '.mp4', '.vob')


class Job:
    def __init__(self, input):
        self.input = input

        if input.startswith('/'):
            self.outdir = os.path.dirname(input)
        else:
            self.outdir = os.getcwd()

        output = os.path.splitext(os.path.basename(input))[0] + ".jpg"
        # I don't know what this is doing...
        self.output = os.path.join(self.outdir, output).replace(r'\ ', ' ')

    def __str__(self):
        return '%s -> %s' % (self.input, self.output)


def _dir_scanner_internal(filename, options, joblist):
    # make sure filename is an absolute path
    if not filename.startswith('/'):
        filename = os.path.join(os.getcwd(), filename)

    # get the extension
    ext = os.path.splitext(filename)[1]

    # if the extension is not supported, return immediately
    if not os.path.isdir(filename) and ext.lower() not in SUPPORTED_EXT:
        logger.error("%s is not supported", filename)
        return

    # recursively scan subdirs
    if os.path.isdir(filename):
        if options.recur:
            if options.verbose:
                logger.info('REC enter %s', filename)
            for f in os.listdir(filename):
                ff = os.path.join(filename, f)
                _dir_scanner_internal(ff, options, joblist)
            if options.verbose:
                logger.info('REC leaving %s', filename)
        else:
            logger.error('%s is a directory', filename)

    joblist.append(Job(filename))


def dir_scanner(filename, options):
    """
    generate a list of jobs as follows: if filename is a supported video file, that will be the only job;
    if @filename is a directory, then recursively add video files in the subdirs to the list.
    :param filename:
    :return:
    """

    joblist = []
    _dir_scanner_internal(filename, options, joblist)

    return joblist