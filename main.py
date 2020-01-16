from utils import download_file
from utils import get_json_from_url
from utils import read_single_keypress
from utils import show_image

import functools
import os
import sty


class Menu:

    def __init__(self):
        self.baseUrl = 'https://pokeapi.co/api/v2'
        self.curOffset = 0
        self.heading = 'SELECT AND PRESS ENTER'
        self.isLoading = False
        self.limitPerPage = 20
        self.options = []
        self.preventNextRender = False
        self.selected = 0
        self.loadPage()

    def loadPage(self):
        self.isLoading = True
        self.render()
        url = '/pokemon/?offset={0}&limit={1}'.format(
            str(self.curOffset), str(self.limitPerPage))
        url = self.baseUrl + url
        data = get_json_from_url(url)
        pokemons = data['results']
        self.options = []
        if self.curOffset > 0:
            self.options.append({
                'label': '[prev page]',
                'onclick': self.loadPrevPage
            })
        for pokemon in pokemons:
            option = {
                'label': pokemon['name'],
                'onclick': functools.partial(self.viewImage, pokemon['url']),
            }
            self.options.append(option)
        self.options.append({
            'label': '[next page]',
            'onclick': self.loadNextPage
        })
        self.isLoading = False
        self.render()

    def loadPrevPage(self):
        self.curOffset -= self.limitPerPage
        if self.curOffset < 0:
            self.curOffset = 0
        self.loadPage()

    def loadNextPage(self):
        self.curOffset += self.limitPerPage
        self.loadPage()

    def viewImage(self, pokemonUrl):
        self.isLoading = True
        self.render()
        data = get_json_from_url(pokemonUrl)
        imgUrl = data['sprites']['front_default']
        tmpFilename = 'tmp.png'
        download_file(imgUrl, tmpFilename)
        self.isLoading = False
        self.render()
        show_image(tmpFilename)
        os.remove(tmpFilename)
        self.preventNextRender = True

    def moveCursorUp(self):
        self.selected -= 1
        if self.selected < 0:
            self.selected = len(self.options) - 1

    def moveCursorDown(self):
        self.selected += 1
        if self.selected > len(self.options) - 1:
            self.selected = 0

    def clickSelection(self):
        option = self.options[self.selected]
        if callable(option['onclick']):
            option['onclick']()

    def render(self):
        if self.preventNextRender:
            self.preventNextRender = False
            return

        os.system('clear')
        print('****{0}****'.format('*' * len(self.heading)))
        print('*** {0} ***'.format(self.heading))
        print('****{0}****'.format('*' * len(self.heading)))
        print('')
        print('--- Press ESC to quit ---')
        print('')

        if self.isLoading:
            print('Loading ...')
            return

        i = 0
        for option in self.options:
            label = option['label']
            if i == self.selected:
                label = sty.bg.blue + sty.fg.white + label + sty.fg.black + sty.bg.rs
            print(label)
            i += 1


KEYS_UP = ('\x1b', '[', 'A')
KEYS_DOWN = ('\x1b', '[', 'B')
KEYS_ENTER = ('\r',)
KEYS_ESC = ('\x1b',)


menu = Menu()

while True:
    menu.render()

    keys = read_single_keypress()
    # print('You pressed: ' + str(keys))

    if keys == KEYS_UP:
        menu.moveCursorUp()
    if keys == KEYS_DOWN:
        menu.moveCursorDown()
    if keys == KEYS_ENTER:
        menu.clickSelection()

    if keys == KEYS_ESC:
        print('\nbye :)')
        break
