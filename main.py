from menu import Menu
from utils import read_single_keypress

import sys


KEYS_UP = ('\x1b', '[', 'A')
KEYS_DOWN = ('\x1b', '[', 'B')
KEYS_ENTER = ('\r',)
KEYS_ESC = ('\x1b',)


if len(sys.argv) > 1:
    langCode = sys.argv[1]

menu = Menu(langCode)
while True:
    menu.render()

    keys = read_single_keypress()

    if keys == KEYS_UP:
        menu.moveCursorUp()
    if keys == KEYS_DOWN:
        menu.moveCursorDown()
    if keys == KEYS_ENTER:
        menu.clickSelection()

    if keys == KEYS_ESC:
        print('\nbye :)')
        break
