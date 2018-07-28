import datetime
import logging
import os
import platform
import tempfile
import numpy as np

import av
from PIL import Image, ImageDraw, ImageFont, ImageOps

logger = logging.getLogger(__name__)


def snapshot(work):
    microseconds, input_filename, output_filename = work
    av_container = av.open(input_filename)
    av_container.seek(microseconds, 'time')
    frame = av_container.decode(video=0).next()
    im = frame.to_image()
    im.save(output_filename)


class Processor:
    num_row = 6
    num_col = 3
    thumb_width = 480

    # up (down), left(right)
    margin = (20, 20)
    vspace = 15
    hspace = 15

    def __init__(self, job, pool, options):
        """ create a Processor instance for job
        :param job
        :type :class:`thumbup.Job`
        :param pool
        :type a thread pool
        :param options:
        """
        # input and output
        self.video_fn = job.input
        self._outdir = job.outdir
        self.snapshot_fn = job.output

        # snapshot options

        # Parse the offset (string)
        def parse_second(string):
            return 1e6 * int(string)

        def _parse_date_str(fmt, string):
            # parse fmt to microseconds
            offset_obj = datetime.datetime.strptime(string, fmt).time()
            # 3600 * seconds + microseconds
            return 1e6 * (offset_obj.hour * 3600 + offset_obj.minute * 60 + offset_obj.second) \
                   + offset_obj.microsecond

        def parse_h_m_s(string):
            # parse "%H:%M:%S.%f" to microseconds
            return _parse_date_str("%H:%M:%S", string)

        def parse_h_m_s_ms(string):
            # parse "%H:%M:%S.%f" to microseconds
            return _parse_date_str("%H:%M:%S.%f", string)

        for i, parser in enumerate((parse_second, parse_h_m_s, parse_h_m_s_ms)):
            try:
                self.offset = parser(options.offset)
                break
            except ValueError:
                if i == 2:
                    raise ValueError("can't parse offset string %s", options.offset)
                else:
                    continue

        self._probe_result = None
        self._cfg_overwrite = options.overwrite

        # open an av container
        # https://mikeboers.github.io/PyAV/api/container.html
        self._av_container = None
        self._threadpool = pool

    def _get_desc(self):
        try:
            vs = self._av_container.streams.video[0]
            dim = '%dx%d' % (vs.width, vs.height)
            codec = '%s, %s' % (vs.name, self._av_container.streams.audio[0].name)
        except av.utils.AVError:
            codec = 'N/A'
            dim = 'N/A'
        return "Filename: %s\nCodec: %s (%s)\n" % (os.path.basename(self.video_fn), codec, dim)

    def run_noexcept(self):
        try:
            self._run()
        except Exception as e:
            logging.error("error: {}".format(e.message))
            return -1

    def _run(self):
        """ execute the processor in one thread

        :return: None
        """
        logger.info("Processing %s" % os.path.basename(self.video_fn))

        if os.path.exists(self.snapshot_fn) and not self._cfg_overwrite:
            logging.info("Thumbnail exists. Skipping... [use -o to overwrite]")
            return 0

        if not self._av_container:
            self._av_container = av.open(self.video_fn)

        duration = self._av_container.duration
        vs = self._av_container.streams.video[0]
        (video_width, video_height) = vs.width, vs.height

        # calculate the thumbnail height in respect to the aspect ratio
        thumb_h = int(self.thumb_width * video_height / video_width)

        # calculate the time (in seconds)
        num_pics = self.num_row * self.num_col
        step = (duration - self.offset) / num_pics
        snapshot_time_list = [int(self.offset + x * step) for x in xrange(0, num_pics)]

        # make temp directory to store tmp pics
        tmp_dir = tempfile.mkdtemp()
        thumbnail_filename_list = [os.path.join(tmp_dir, "%d.jpg" % x) for x in xrange(0, num_pics)]

        # taking snapshot in many threads
        works = [(time, self.video_fn, thumbnail_filename_list[idx]) for idx, time in enumerate(snapshot_time_list)]

        # run procedure in a thread tool
        self._threadpool.map(snapshot, works)

        # Concat thumbnails
        pic_height = int(self.num_row * thumb_h + 2 * self.margin[0] + self.vspace * (self.num_row - 1))
        pic_width = int(self.num_col * self.thumb_width + 2 * self.margin[1] + self.hspace * (self.num_col - 1))

        # create a new image
        output_img = Image.new(mode='RGB', size=(pic_width, pic_height), color='white')

        # load font
        system_id = platform.system()
        if system_id == 'Linux':
            default_font = 'cour.ttf'
        elif system_id == 'Darwin':
            default_font = 'Helvetica'

        try:
            font = ImageFont.truetype(default_font, size=20)
        except IOError as e:
            logging.warn("can't load font {}. Fall back to default".format(e.message))
            font = ImageFont.load_default()

        output_draw = ImageDraw.Draw(output_img)
        output_draw.text((self.margin[1], self.margin[0]), text=self._get_desc(), fill=(0, 0, 0), font=font)

        y_offset_for_text = 50

        for i in xrange(0, self.num_row):
            for j in xrange(0, self.num_col):
                x = int(self.margin[1] + j * (self.thumb_width + self.vspace))
                y = int(self.margin[0] + y_offset_for_text + i * (thumb_h + self.hspace))
                try:
                    im = Image.open(thumbnail_filename_list[i * self.num_col + j])
                    # down sample
                    im.thumbnail((self.thumb_width, thumb_h))

                    # add frame
                    im = ImageOps.expand(im, border=2, fill='#aaa')

                    # add text to small thumbnails
                    left_top_corner = im.crop((0, 0, 100, 50))
                    # compute average color
                    average_color = tuple(np.mean(np.array(left_top_corner), axis=(0, 1), dtype=int))

                    # ((Red value X 299) + (Green value X 587) + (Blue value X 114)) / 1000
                    brightness = (average_color[0] * 299 + average_color[1] * 587 + average_color[2] * 114) / 1000
                    text_color = (255, 255, 255) if brightness < 150 else (0, 0, 0)
                    tick = snapshot_time_list[i * self.num_col + j]
                    draw = ImageDraw.Draw(im)
                    draw.text((10, 10), text=str(datetime.timedelta(microseconds=tick)), font=font, fill=text_color)
                    del draw
                except IOError as e:
                    logging.error("Can't gen thumbnail for ({}, {}): {}".format(i, j, e.message))
                    continue
                output_img.paste(im, (x, y))

        output_img.save(self.snapshot_fn)

        for o in thumbnail_filename_list:
            try:
                os.remove(o)
            except OSError as e:
                continue
