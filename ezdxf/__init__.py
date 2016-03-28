# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

version = (0, 7, 5)  # also update VERSION in setup.py
VERSION = "%d.%d.%d" % version
__version__ = VERSION
__author__ = "mozman <mozman@gmx.at>"

import sys
if sys.version_info[:2] < (2, 7):
    raise ImportError("Package 'ezdxf' requires Python 2.7 or later!")

import io

from .lldxf import encoding
from .options import options  # example: ezdxf.options.template_dir = 'c:\templates'
from .lldxf.tags import dxf_info
from .lldxf.tags import TagIterator
from .tools.importer import Importer
from .lldxf.const import DXFStructureError, DXFVersionError, DXFStreamError
from .tools.zipmanager import ctxZipReader
from .tools import transparency2float, float2transparency  #  convert transparency integer values to floats 0..1
from .tools.rgb import int2rgb, rgb2int
from .tools.pattern import PATTERN
from .lldxf import const  #  restore module structure ezdxf.const


def new(dxfversion='AC1009'):
    """Create a new DXF drawing.

    :param dxfversion: DXF version specifier, default is 'AC1009'

    new() can create drawings for following DXF versions:
    - 'AC1009': AutoCAD R12 (DXF12)
    - 'AC1015': AutoCAD 2000
    - 'AC1018': AutoCAD 2004
    - 'AC1021': AutoCAD 2007
    - 'AC1024': AutoCAD 2010
    - 'AC1027': AutoCAD 2013

    """
    from .drawing import Drawing
    return Drawing.new(dxfversion)

# TODO: read DXF stream as binary data and decode each line individually
# some string tags seems to be written with the encoding settings of the DXF header,
# some other strings (layer name) seems to be encoded as unicode strings.
# And this may differ for older and newer DXF versions.


def read(stream):
    """Read DXF drawing from a binary *stream*, which only needs a readline() method.

    read() can open drawings of following DXF versions:
    - pre 'AC1009' DXF versions will be read as 'AC1009'
    - 'AC1009': AutoCAD R12 (DXF12)
    - 'AC1012': AutoCAD R12 converted to AC1015
    - 'AC1014': AutoCAD R14 converted to AC1015
    - 'AC1015': AutoCAD 2000
    - 'AC1018': AutoCAD 2004
    - 'AC1021': AutoCAD 2007
    - 'AC1024': AutoCAD 2010
    - 'AC1027': AutoCAD 2013

    """
    from .drawing import Drawing
    return Drawing.read(stream)


def readfile(filename):
    """Read DXF drawing from file *filename*.
    """
    if not is_dxf_file(filename):
        raise IOError("File '{}' is not a DXF file.".format(filename))

    with io.open(filename, mode='rt', encoding='utf-8', errors='ignore') as fp:
        info = dxf_info(fp)

    if info.version >= 'AC1021':  # R2007 or newer always encoded as utf-8
        enc = 'utf-8'
    else:
        enc = info.encoding

    with io.open(filename, mode='rt', encoding=enc, errors='dxfreplace') as fp:
        dwg = read(fp)

    dwg.filename = filename
    return dwg


def readzip(zipfile, filename=None):
    """ Reads the DXF file *filename* from *zipfile* or the first DXF file in *zipfile* if *filename* is *None*.
    """
    with ctxZipReader(zipfile, filename) as zipstream:
        dwg = read(zipstream)
        dwg.filename = zipstream.dxf_file_name
    return dwg


def is_dxf_file(filename):
    with io.open(filename, errors='ignore') as fp:
        reader = TagIterator(fp)
        return next(reader) == (0, 'SECTION')
