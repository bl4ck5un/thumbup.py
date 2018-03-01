import os
import subprocess as sp
import json
import math
import logging
import sys
import tempfile
import shlex
import multiprocessing
from PIL import Image, ImageDraw, ImageFont

num_row = 6
num_col = 3
thumb_width = 360
recursive = True
verbose = False

# up (down), left(right)
margin = (20, 20)
vspace = 10
hspace = 10


def snapshot(job):
    tick, inputname, w, h, outputname = job
    cmd = "ffmpeg -ss %d -i '%s' -vframes 1 -f image2 -s %dx%d -loglevel quiet -y %s" % \
          (tick, inputname, w, h, outputname)
    try:
        logging.info("running: %s", cmd)
        sp.check_call(shlex.split(cmd))
        sys.stdout.write(".")
        sys.stdout.flush()
    except sp.CalledProcessError as e:
        print 'ERR unable to run %s, msg: %s' % (cmd, e.message)
        print e.output
        print e.returncode
        return -1


class Processor:
    def __init__(self, job, threadpool, options):
        # input and output
        self.video_fn = job.input
        self._outdir = job.outdir
        self.snapshot_fn = job.output

        # snapshot options
        self.offset = options.offset

        self.threadpool = threadpool

        self._probe_result = None
        self._cfg_overwrite = options.overwrite

    def _get_duration(self):
        """
        :return: the duration in seconds
        """
        if not self._probe_result:
            self.probe()

        return int(float(self._probe_result["format"]["duration"]))

    def _get_dimension(self):
        """
        :return: the dimension in (width, height)
        """
        if not self._probe_result:
            self.probe()

        streams = self._probe_result["streams"]
        assert streams

        video_streams = filter(lambda x: x["codec_type"] == "video", streams)
        if len(video_streams) > 1:
            logging.warn("%d streams detected", len(video_streams))

        video_streams = video_streams[0]
        return map(int, (video_streams["width"], video_streams["height"]))

    def probe(self):
        if not os.path.exists(self.video_fn):
            raise Exception('Gvie ffprobe a full file path of the video')

        command = ["ffprobe",
                   "-loglevel", "quiet",
                   "-print_format", "json",
                   "-show_format",
                   "-show_streams",
                   self.video_fn
                   ]

        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
        out, err = pipe.communicate()
        if (err):
            print err
            raise Exception(err)
        try:
            self._probe_result = json.loads(out)
        except:
            raise Exception("%s: can't parse JSON: %s" % (' '.join(command), out))

    def run(self):
        sys.stdout.write("GEN %s " % self.video_fn)
        sys.stdout.flush()

        if os.path.exists(self.snapshot_fn) and not self._cfg_overwrite:
            print '... skipping...'
            return 0

        duration = self._get_duration()
        (video_width, video_height) = self._get_dimension()

        # calculate the thumbnail height in respect to the aspect ratio
        thumb_height = int(thumb_width * video_height / video_width)

        num_pics = num_row * num_col
        checkpoint = [int(math.floor(duration * x / num_pics)) for x in xrange(0, num_pics)]

        checkpoint[0] += self.offset

        # make temp directory to store tmp pics
        tmpd = tempfile.mkdtemp()
        small_thumbnails = [os.path.join(tmpd, "%d.jpg" % x) for x in xrange(0, num_pics)]

        jobs = []
        for idx, time in enumerate(checkpoint):
            jobs.append((time, self.video_fn, thumb_width, thumb_height, small_thumbnails[idx]))

        self.threadpool.map(snapshot, jobs)

        # Concat
        pic_height = int(num_row * thumb_height + 2 * margin[0] + vspace * (num_row - 1))
        pic_width = int(num_col * thumb_width + 2 * margin[1] + hspace * (num_col - 1))

        # create a new image
        output_img = Image.new(mode='RGB', size=(pic_width, pic_height), color='white')

        # load font
        # font = ImageFont.truetype("arial.ttf", 15)

        for i in xrange(0, num_row):
            for j in xrange(0, num_col):
                x = int(margin[1] + j * (thumb_width + vspace))
                y = int(margin[0] + i * (thumb_height + hspace))
                try:
                    im = Image.open(small_thumbnails[i * num_col + j])

                    # add text to small thumbnails
                    import datetime
                    tick = checkpoint[i * num_col + j]
                    draw = ImageDraw.Draw(im)
                    draw.text((10, 10), text=str(datetime.timedelta(seconds=tick)))#, font=font)
                    del draw
                except IOError as e:
                    print e.strerror
                    continue
                im.thumbnail((thumb_width, thumb_height))
                output_img.paste(im, (x, y))

        output_img.save(self.snapshot_fn)

        for o in small_thumbnails:
            try:
                os.remove(o)
            except OSError as e:
                continue

        sys.stdout.write('\n')
