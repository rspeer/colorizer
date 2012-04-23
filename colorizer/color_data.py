from pkg_resources import resource_filename, resource_stream
from collections import defaultdict
from conceptnet.models import Assertion, Language
from csc_utils.persist import PickleDict
from colormath.color_objects import LuvColor, LabColor, RGBColor
import numpy as np
import cPickle as pickle
import logging
import random
import math

def rgb_to_luv(rgb):
    rgbcolor = RGBColor(*rgb)
    luvcolor = rgbcolor.convert_to('xyz').convert_to('luv')
    return (luvcolor.luv_l, luvcolor.luv_u, luvcolor.luv_v)

def rgb_to_wheel(rgb):
    rgbcolor = RGBColor(*rgb)
    hsvcolor = rgbcolor.convert_to('hsv')
    angle = hsvcolor.hsv_h*2*math.pi/360
    return (math.sin(angle) * hsvcolor.hsv_s, math.cos(angle) * hsvcolor.hsv_s)

def lab_to_hsv(lab):
    labcolor = LabColor(*lab)
    hsvcolor = labcolor.convert_to('hsv')
    return (hsvcolor.hsv_h, hsvcolor.hsv_s, hsvcolor.hsv_v)

def rgb_to_lab(rgb):
    rgbcolor = RGBColor(*rgb)
    labcolor = rgbcolor.convert_to('lab')
    return (labcolor.lab_l, labcolor.lab_a, labcolor.lab_b)

def rgb_to_hsv(rgb):
    rgbcolor = RGBColor(*rgb)
    hsvcolor = rgbcolor.convert_to('hsv')
    return (hsvcolor.hsv_l, hsvcolor.hsv_a, hsvcolor.hsv_b)

def lab_to_rgb(lab):
    labcolor = LabColor(*lab)
    rgbcolor = labcolor.convert_to('rgb')
    return (rgbcolor.rgb_r, rgbcolor.rgb_g, rgbcolor.rgb_b)

def luv_to_rgb(luv):
    luvcolor = LuvColor(*luv)
    rgbcolor = luvcolor.convert_to('rgb')
    return (rgbcolor.rgb_r, rgbcolor.rgb_g, rgbcolor.rgb_b)

log = logging.getLogger('colorizer')
log.setLevel(logging.INFO)
logging.basicConfig()

pd = PickleDict(resource_filename('colorizer', 'pickledata'))

colorlist = ['blue', 'black', 'brown', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
rgb = {'blue': (0,0,255), 'black': (0,0,0), 'brown': (139, 69, 19), 'green': (0, 255, 0), 'grey': (100,100,100), 'orange': (255, 165,0), 'pink': (255,105,180), 'purple': (160, 32, 240), 'red': (255,0,0), 'white': (255, 255, 255), 'yellow': (255,255,0)}
en = Language.get('en')

def total_distance(array, vec):
    return np.sum(np.sqrt(np.sum((array-vec)**2, axis=1)))

def medianesque(array):
    """
    Given a bunch of vector values (such as colors), return the one closest
    to the median. Samples an arbitrary 100 colors if there are too many to
    analyze efficiently.
    """
    if len(array) > 100: array = random.sample(array, 100)
    array = np.asarray(array)
    distances = [total_distance(array, array[i]) for i in xrange(array.shape[0])]
    return array[np.argmin(distances)]

def component_median(array):
    return np.median(array, axis=0)

@pd.lazy(version=1)
def xkcd_data():
    xkcd = defaultdict(list)

    with open('grouped_color_data.txt') as inputlines:
        for line in inputlines:
            try:
                colorname, userid, r, g, b, monitor, colorblind, male = line.strip().split('|')
            except ValueError:
                continue
            rgblist = [float(r), float(g), float(b)]
            xkcd[colorname].append(rgblist)
            print colorname.decode('utf-8').encode('ascii', 'replace')
    return xkcd

def make_lab_color_data():
    """
    Returns a dictionary mapping color names to lists of Lab color values.
    """
    return pickle.load(open('pickledata/make_lab_color_data'))

def nearest_color(colormat, rgb):
    lab = rgb_to_lab(rgb)
    diffs = np.abs(colormat[:,:3] - lab)
    distances = np.sum(diffs, axis=-1)
    best = np.argmin(distances)
    return colormat.row_label(best)

