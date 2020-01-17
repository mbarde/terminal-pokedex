from PIL import Image

import json
import numpy
import urllib3


def get_ansi_color_code(r, g, b):
    if r == g and g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)


def get_color(r, g, b):
    return "\x1b[48;5;{}m \x1b[0m".format(int(get_ansi_color_code(r, g, b)))


# https://github.com/nikhilkumarsingh/terminal-image-viewer
def show_image(img_path, menu, max_height=False):
    try:
        img = Image.open(img_path).convert('RGBA')
    except FileNotFoundError:
        exit('Image not found.')

    # auto crop (remove empty border)
    imageBox = img.getbbox()
    img = img.crop(imageBox)

    # transparent background should be displayed white
    img = Image.composite(img, Image.new('RGBA', img.size, 'white'), img)

    # resize
    if max_height is not False and max_height < img.height:
        h = max_height
        w = int((img.width / img.height) * h)
        img = img.resize((w, h), Image.ANTIALIAS)

    img_arr = numpy.asarray(img)
    h, w, c = img_arr.shape

    for x in range(h):
        line = ''
        for y in range(w):
            pix = img_arr[x][y]
            # print(get_color(pix[0], pix[1], pix[2]), end='')
            line += get_color(pix[0], pix[1], pix[2])
        menu.appendLine(line, (40, x))
        # print()


# https://stackoverflow.com/a/6599441
def read_single_keypress():
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns a tuple of characters of the key that was pressed - on Linux,
    pressing keys like up arrow results in a sequence of characters. Returns
    ('\x03',) on KeyboardInterrupt which can happen when a signal gets
    handled.

    """
    import fcntl
    import os
    import sys
    import termios
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save)  # copy the stored version to update
    # iflag
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR
                  | termios.ICRNL | termios.IXON)
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    ret = []
    try:
        ret.append(sys.stdin.read(1))  # returns a single character
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
        c = sys.stdin.read(1)  # returns a single character
        while len(c) > 0:
            ret.append(c)
            c = sys.stdin.read(1)
    except KeyboardInterrupt:
        ret.append('\x03')
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return tuple(ret)


def get_json_from_url(url):
    http = urllib3.PoolManager()
    res = http.request('GET', url)
    jsonData = json.loads(res.data)
    res.release_conn()
    return jsonData


def download_file(url, filename):
    http = urllib3.PoolManager()
    res = http.request('GET', url, preload_content=False)
    with open('tmp.png', 'wb') as out:
        while True:
            data = res.read(65536)  # 65Kb
            if not data:
                break
            out.write(data)
    res.release_conn()
