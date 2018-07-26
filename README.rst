thumbup
=======
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
  
``ffmpeg`` is also widely available for many other distros. Please refer to the official website https://www.ffmpeg.org/download.html.

``thumbup`` can be installed from ``pip`` by

.. code-block::

  pip install thumbup

Usage
-----

To generate thumbnails for video files, use

.. code-block::

  thumbup file1 file2

The above will create ``file1.jpg`` and ``file2.jpg``.

To generate thumbnails for all video files in directory ``dir``, use ``-R`` option. ``thumbup`` will recursively go through every video in directory ``dir`` and generate thumbnails next to them.

.. code-block::

  thumbup -R dir
