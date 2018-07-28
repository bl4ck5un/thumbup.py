thumbup :thumbsup:
==================
.. image:: https://badge.fury.io/py/thumbup.svg
    :alt: pypi
    :target: https://badge.fury.io/py/thumbup
.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :alt: license
    :target: https://opensource.org/licenses/MIT
.. image:: https://travis-ci.org/bl4ck5un/thumbup.py.svg?branch=master
    :alt: travis-ci
    :target: https://travis-ci.org/bl4ck5un/thumbup.py


``thumbup`` is a command-line video thumbnails generator written in Python.

Getting thumbup
---------------

You'll need ``ffmpeg`` before you can use ``thumbup``, which can be installed by

.. code-block::

  # on macOS
  brew install ffmpeg

  # on ubuntu (>= 14.04)
  sudo apt-get install -y \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
  
``ffmpeg`` is also widely available for many other distros. Please refer to the official website https://www.ffmpeg.org.

``thumbup`` can be installed from ``pip`` by

.. code-block::

  pip install thumbup

Usage
-----

To generate thumbnails for video files ``file1`` and ``file2``, simply use

.. code-block::

  thumbup file1 file2

The above will create ``file1.jpg`` and ``file2.jpg`` in the same directory as the video files.

To generate thumbnails for all video files in directory ``dir``, use ``-r`` option. ``thumbup`` will recursively go through every video in directory ``dir`` and generate thumbnails next to them.

.. code-block::

  thumbup -r dir

Full help message for more control:


.. code-block::

    usage: thumbup.py [-h] [-v] [-r] [-f] [-o OFFSET] [-s X] FILE [FILE ...]

    thumbup video thumbnail generator v1.2.0

    positional arguments:
      FILE                  one or more video files or directories (with -r)

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         logging more stuff
      -r, --rec             recursively go into all dirs
      -f, --force           force overwrite existing thumbnails
      -o OFFSET, --offset OFFSET
                            skip OFFSET (hh:mm:ss.ms or second) from the beginning
      -s X, --suffix X      add suffix to the output filename, input.mp4 ->
                            inputX.jpg
