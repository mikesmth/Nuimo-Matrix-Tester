#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys


class CharacterGenerator(object):
    global charCodeOrd

    def __init__(self):
        global f
        self.charCodeOrd = 0
        f = open('./bin/fonts')

    def get_matrix_ord(self, charCode):
        self.charCodeOrd = charCode
        f.seek(charCode * ((4 * 8) + 8))
        #                  |______|  |_|
        #                   4 char    whitespace
        row = f.read((4 * 8) + (1 * 8))
        matrix = row.split()
        matrix = map(lambda x: bin(int(x, 16))[2:].zfill(8)[::1], matrix)
        # change matrix  to 9x9 format (source is 8x8)
        for idx, item in enumerate(matrix):
            matrix[idx] = "0" + item
        matrix.insert(0, "000000000")
        return matrix

    def get_matrix(self, char):
        charCode = self.get_ord(char)
        return self.get_matrix_ord(charCode)

    def get_matrix_string(self, charCode):
        matrix = self.get_matrix(charCode)
        return ''.join(matrix).replace('1', '*').replace('0', ' ')

    def get_matrix_string_ord(self, charCode):
        matrix = self.get_matrix_ord(charCode)
        return ''.join(matrix).replace('1', '*').replace('0', ' ')

    @staticmethod
    def get_ord(char):
        # slightly adjusted combined code pages cp866 (http://caxapa.ru/149446.html)
        # ToDo: change to adhere standard codepages including cp866
        chars = u" ☺☻♥♦♣♠⋅◘○⧖♂♀♪☀☼◀▶↕‼π§₌↨↑↓→←⌞↔▲▼ " \
                u"!\"#$%&'()*+,-./0123456789:;<=>?@" \
                u"ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`" \
                u"abcdefghijklmnopqrstuvwxyz{|}~" \
                u"░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬ " \
                u"╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ " \
                u"АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" \
                u"абвгдежзийклмнопрстуфхцчшщъыьэюяЁёЄє"
        chr_arr = []
        for i in chars:
            chr_arr.append(repr(i))
        try:
            index = chr_arr.index(str(repr(char)))

            return index
        except ValueError:
            # can't find some character, just return a space char for now
            # change to 63 for '?'
            return 0
