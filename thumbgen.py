#!/usr/bin/python
# generate thumbnails

from PIL import Image
from os import listdir
from os.path import isfile, join
import numpy
import subprocess as sp
import sys
from math import floor
import json
import shlex
import os
import tempfile
import re

num_row = 5
num_col = 3
thumb_width = 360
offset = 60

def run(filename):
    if filename.startswith('/'):
        outd = os.path.dirname(filename)
    else:
        outd = os.getcwd()

    sys.stdout.write("Generating thumbnails for %s " % filename)

    cmd = 'ffprobe %s' % filename
    pipe = sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.STDOUT)
    meta = pipe.stdout.readlines()


    re_du = re.compile(r'Duration:(.*?),')
    re_size = re.compile(r'(\d{3,})x(\d{3,})')

    duration = [x for x in meta if re_du.search(x) is not None]
    try:
        assert len(duration) == 1
    except:
        print duration
        sys.exit()
    duration = duration[0]

    size = [x for x in meta if re_size.search(x) is not None]
    try:
        assert len(size) == 1
    except:
        print size
        sys.exit()
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


    tmpd = tempfile.mkdtemp()
    outputs = [os.path.join(tmpd, "%d.png" % x) for x in xrange(0, num_pics)]



    # Let's take snapshots
    procs = []
    for idx, time in enumerate(checkpoint):
            hh = time/3600
            mm = (time%3600)/60
            ss = time%60
            fill = (hh, mm, ss, filename, outputs[idx])
            cmd = "ffmpeg -ss %d:%d:%d -i %s -vframes 1 -loglevel error -y %s" % fill
            #print cmd
            sys.stdout.write(".")
            sp.Popen(shlex.split(cmd)).wait()


    for proc in procs:
            pass



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


    out_filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
    new_im.save(os.path.join(outd, out_filename))
    for o in outputs:
            os.remove(o)

    sys.stdout.write(' Done.\n')
    sys.stdout.flush()

if len(sys.argv) > 1:
    for filename in sys.argv[1:]:
        run(filename)
else:
    try:
        while True:
            filename = raw_input('Filename: ')
            run(filename)
    except (EOFError, KeyboardInterrupt):
        os.sys.stdout.write('\nDone.\n')
