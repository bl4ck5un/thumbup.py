import os
import logging
import tempfile

import av
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

logger = logging.getLogger(__name__)


def snapshot(work):
    tick, input_filename, output_filename = work
    av_container = av.open(input_filename)
    av_container.seek(tick * 1000000, 'time')
    frame = av_container.decode(video=0).next()
    im = frame.to_image()
    im.save(output_filename)


class Processor:
    """
    Processor
    """

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
        self.offset = options.offset

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
        return """Filename: %s\nCodec: %s (%s)\n""" % (os.path.basename(self.video_fn), codec, dim)

    def run_noexcept(self):
        try:
            self._run()
        except Exception as e:
            print e.message
            return -1

    def _run(self):
        """ execute the processor in one thread

        :return: None
        """
        logger.info("Processing %s" % os.path.basename(self.video_fn))

        if os.path.exists(self.snapshot_fn) and not self._cfg_overwrite:
            logging.info("skipping...")
            return 0

        if not self._av_container:
            self._av_container = av.open(self.video_fn)

        duration = self._av_container.duration / 1e6
        vs = self._av_container.streams.video[0]
        (video_width, video_height) = vs.width, vs.height

        # calculate the thumbnail height in respect to the aspect ratio
        thumb_h = int(thumb_width * video_height / video_width)

        # calculate the time (in seconds)
        num_pics = num_row * num_col
        step = (duration - self.offset) / num_pics
        snapshot_time_list = [int(self.offset + x * step) for x in xrange(0, num_pics)]

        # make temp directory to store tmp pics
        tmp_dir = tempfile.mkdtemp()
        thumbnail_filename_list = [os.path.join(tmp_dir, "%d.jpg" % x) for x in xrange(0, num_pics)]

        # taking snapshot in many threads
        works = [(time, self.video_fn, thumbnail_filename_list[idx]) for idx, time in enumerate(snapshot_time_list)]
        self._threadpool.map(snapshot, works)

        # Concat thumbnails
        pic_height = int(num_row * thumb_h + 2 * margin[0] + vspace * (num_row - 1))
        pic_width = int(num_col * thumb_width + 2 * margin[1] + hspace * (num_col - 1))

        # create a new image
        output_img = Image.new(mode='RGB', size=(pic_width, pic_height), color='white')

        # load font
        font = ImageFont.load_default()

        output_draw = ImageDraw.Draw(output_img)
        output_draw.text((margin[1], margin[0]), text=self._get_desc(), fill=(0, 0, 0), font=font)

        y_offset_for_text = 50

        for i in xrange(0, num_row):
            for j in xrange(0, num_col):
                x = int(margin[1] + j * (thumb_width + vspace))
                y = int(margin[0] + y_offset_for_text + i * (thumb_h + hspace))
                try:
                    im = Image.open(thumbnail_filename_list[i * num_col + j])
                    im.thumbnail((thumb_width, thumb_h))

                    # add text to small thumbnails
                    import datetime
                    tick = snapshot_time_list[i * num_col + j]
                    draw = ImageDraw.Draw(im)
                    draw.text((10, 10), text=str(datetime.timedelta(seconds=tick)), font=font)
                    del draw
                except IOError as e:
                    print e.strerror
                    continue
                output_img.paste(im, (x, y))

        output_img.save(self.snapshot_fn)

        for o in thumbnail_filename_list:
            try:
                os.remove(o)
            except OSError as e:
                continue
