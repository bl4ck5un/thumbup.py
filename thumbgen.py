#!/usr/bin/python
# generate thumbnails

from PIL import Image
from os import listdir
from os.path import isfile, join
import subprocess as sp
import sys
from math import floor
import json
import shlex
import os
import tempfile
import re
import getopt

num_row = 5
num_col = 3
thumb_width = 360
offset = 60
dry_run = False
recursive = True


def run(filename):

    # basename
    _filename = os.path.basename(filename)

    # recursive if configured
    if os.path.isdir(filename):
        if recursive:
            print 'REC enter %s' % filename
            for f in os.listdir(filename):
                ff = os.path.join(filename, f)
                print 'REC %s' % f
                run(ff)
            print 'REC leave %s' % filename

    # check support
    ext = os.path.splitext(filename)[1]
    if ext not in ('.m4v', '.wmv', '.avi', '.mkv', '.mp4'):
        print 'ERR file %s not supported' % _filename
        return -1

    if filename.startswith('/'):
        outd = os.path.dirname(filename)
    else:
        outd = os.getcwd()

    out_filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
    outfile = os.path.join(outd, out_filename).replace(r'\ ', ' ')

    if os.path.exists(outfile):
        print 'WARN %s existes' % os.path.basename(outfile)
        return -1

    if dry_run:
        print 'Output writes to %s' % outfile
        return 0

    # getting duration and frame size
    cmd = 'ffprobe \'%s\'' % filename
    pipe = sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.STDOUT)
    meta = pipe.stdout.readlines()

    re_du = re.compile(r'Duration:(.*?),')
    re_size = re.compile(r'(\d{3,})x(\d{3,})')

    duration = [x for x in meta if re_du.search(x) is not None]
    try:
        assert len(duration) == 1
    except:
        print 'Can\'t get duration %s' % str(duration)
        print cmd
        print meta
        return -1
    duration = duration[0]

    size = [x for x in meta if re_size.search(x) is not None]
    try:
        assert len(size) >= 1
    except:
        print 'ERR can\'t get size'
        for s in size:
            sys.stdout.write(s)
        return -1
    size = size[0]

    hhmmss = re_du.search(duration).group(1).strip()
    (hh,mm,ss) = [int(x) for x in re.compile(r'(\d{2}):(\d{2}):(\d{2}).\d+').match(hhmmss).groups()]
    (w,h) = [int(x) for x in re_size.search(size).groups()]

    # read in some information
    duration = hh*3600 + mm*60 + ss
    video_height = h
    video_width = w

    thumb_height = int(thumb_width * video_height / video_width)

    num_pics = num_row*num_col
    checkpoint = [int(floor(duration*x/num_pics)) for x in xrange(0, num_pics)]

    checkpoint[0] += offset

    # make temp directory to store tmp pics
    tmpd = tempfile.mkdtemp()
    outputs = [os.path.join(tmpd, "%d.png" % x) for x in xrange(0, num_pics)]

    # Let's take snapshots
    sys.stdout.write("GEN %s " % filename)
    sys.stdout.flush()
    procs = []
    for idx, time in enumerate(checkpoint):
        hh = time/3600
        mm = (time%3600)/60
        ss = time%60
        fill = (hh, mm, ss, filename, outputs[idx])
        cmd = "ffmpeg -ss %d:%d:%d -i '%s' -vframes 1 -loglevel quiet -y %s" % fill
        sys.stdout.write(".")
        try:
            sp.check_call(shlex.split(cmd))
        except sp.CalledProcessError:
            print 'ERR unable to run %s' % cmd
            return -1


    # Concat
    # up (down), left(right)
    margin = [50, 20]
    vspace = 5
    hspace = 5

    pic_height = int(num_row * thumb_height + 2*margin[0] + vspace * (num_row - 1))
    pic_width = int(num_col * thumb_width + 2*margin[1] + hspace * (num_col - 1))


    new_im = Image.new('RGB', (pic_width, pic_height))

    for i in xrange(0, num_row):
            for j in xrange(0, num_col):
                    x = int(margin[1] + j*(thumb_width + vspace))
                    y = int(margin[0] + i*(thumb_height + hspace))
                    im = Image.open(outputs[i*num_col + j])
                    im.thumbnail((thumb_width, thumb_height))
                    new_im.paste(im, (x,y))

    new_im.save(outfile)

    for o in outputs:
            os.remove(o)

    sys.stdout.write(' Done.\n')
    sys.stdout.flush()


#---------------- main ------------------#
try:
    opts, remainder = getopt.getopt(sys.argv[1:], 'r:c:w:o:n', ['dry-run'])
    for opt, arg in opts:
        if opt in ('--dry-run', '-n'):
            dry_run = True
except getopt.GetoptError:
    print 'Usage'
    sys.exit(-1)

try:
    if remainder:
        for filename in remainder:
            print 'REC enter %s' % os.path.dirname(filename)
            run(filename)
    else:
        while True:
            filename = raw_input('Filename: ')
            run(filename)
except (EOFError, KeyboardInterrupt):
    os.sys.stdout.write('\nDone.\n')
