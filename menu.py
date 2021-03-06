from utils import download_file
from utils import get_json_from_url
from utils import get_poke_name_by_language
from utils import is_valid_lang_code
from utils import remove_ansi_clr_codes
from utils import show_image

import functools
import os
import random
import sty


class Menu:

    def __init__(self, languageCode='en'):
        self.baseUrl = 'https://pokeapi.co/api/v2'
        self.curOffset = 0
        self.isLoading = False
        self.language = 'en'
        if is_valid_lang_code(languageCode):
            self.language = languageCode
        self.heading = 'SELECT AND PRESS ENTER (lang: {0})'.format(self.language)
        self.limitPerPage = 20
        self.options = []
        self.preventNextRender = False
        self.virtualLines = []
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
        else:
            self.options.append({
                'label': '[RANDOM]',
                'onclick': self.viewRandomImage
            })
        for pokemon in pokemons:
            pokemonData = get_json_from_url(pokemon['url'])
            option = {
                'label': get_poke_name_by_language(pokemonData, self.language),
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

        if imgUrl is None:
            self.isLoading = False
            name = get_poke_name_by_language(data, self.language)
            msg = 'Found no sprite for {0} (#{1}) :('.format(name.capitalize(), data['id'])
            self.clearVirtualLines()
            self.writeMenu()
            self.insertIntoVirtualLines(msg, offset=(40, 5))
            self.renderVirtualLines()
            self.preventNextRender = True
            return

        tmpFilename = 'tmp.png'
        download_file(imgUrl, tmpFilename)

        self.isLoading = False
        self.clearVirtualLines()
        self.writeMenu()

        _, terminalHeight = os.get_terminal_size()
        show_image(data, tmpFilename, self, offset=(40, 0), max_height=terminalHeight-3)
        os.remove(tmpFilename)

        self.renderVirtualLines()
        self.preventNextRender = True

    def viewRandomImage(self):
        url = self.baseUrl + '/pokemon?offset=0&limit=1000'
        all = get_json_from_url(url)['results']
        rPokemon = random.choice(all)
        self.viewImage(rPokemon['url'])

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

    def clearVirtualLines(self):
        self.virtualLines = []

    def appendLine(self, line):
        self.virtualLines.append(line)

    # insert text at specified offset within the virtual lines
    def insertIntoVirtualLines(self, text, offset):
        if len(offset) < 2:
            return

        offX = offset[0]
        offY = offset[1]

        # fill vertical if necessary
        if offY > len(self.virtualLines) - 1:
            toFill = offY - len(self.virtualLines) + 1
            self.virtualLines += [''] * toFill

        virtualLine = self.virtualLines[offY]
        clearVirtualLine = remove_ansi_clr_codes(virtualLine)

        # fill horizontal if necessary
        if offX > len(clearVirtualLine):
            toFill = (offX - len(clearVirtualLine)) - 1
            virtualLine += ' ' * toFill

        diffLen = len(virtualLine) - len(clearVirtualLine)
        virtualLine = virtualLine[:offX + diffLen] + text
        self.virtualLines[offY] = virtualLine

    def renderVirtualLines(self):
        self.clear()
        for line in self.virtualLines:
            print(line)

    def writeHeader(self):
        lenHeading = len(remove_ansi_clr_codes(self.heading))
        self.appendLine('****{0}****'.format('*' * lenHeading))
        self.appendLine('*** {0} ***'.format(self.heading))
        self.appendLine('****{0}****'.format('*' * lenHeading))
        self.appendLine('')
        self.appendLine('--- Press ESC to quit ---')
        self.appendLine('')

    def writeOptions(self):
        i = 0
        for option in self.options:
            label = option['label']
            if i == self.selected:
                label = sty.bg.blue + sty.fg.white + label + sty.fg.rs + sty.bg.rs
            self.appendLine(label)
            i += 1

    def writeMenu(self):
        self.writeHeader()

        if self.isLoading:
            self.appendLine('Loading ...')
        else:
            self.writeOptions()

    def render(self):
        if self.preventNextRender:
            self.preventNextRender = False
            return

        self.clearVirtualLines()
        self.writeMenu()
        self.renderVirtualLines()

    def clear(self):
        os.system('clear')
