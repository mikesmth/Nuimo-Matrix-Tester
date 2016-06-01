#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import platform as _platform
from lib.font_to_matrix import CharacterGenerator
from PyQt4.QtCore import QThread

import time

try:
    from bluepy.btle import UUID, DefaultDelegate, Peripheral, BTLEException
    from lib.nuimo import NuimoDelegate, Nuimo
except ImportError as e:
    if _platform == "darwin":
        print("Warning: Limited functionality: Can't connect to Nuimo on OS X!")


        def UUID(s):
            return s
    else:
        print("Failed to import bluepy library")
        raise e

import sys
from PyQt4 import QtGui, QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class LedMatrix:
    global nuimo
    global charGen

    def __init__(self):
        self.charGen = CharacterGenerator()

        if _platform != "darwin":
            self.nuimo = Nuimo(sys.argv[1])

            if len(sys.argv) < 2:
                print("Usage: python nuimo_matrix.py <Nuimo's MAC address>")
                sys.exit()

            # Connect to Nuimo
            print("Trying to connect to %s. Press Ctrl+C to cancel." % sys.argv[1])
            try:
                self.nuimo.connect()
            except BTLEException:
                print(
                    "Failed to connect to %s. Make sure to:\n  "
                    "1. Disable the Bluetooth device: hciconfig hci0 down\n  "
                    "2. Enable the Bluetooth device: hciconfig hci0 up\n  "
                    "3. Enable BLE: btmgmt le on\n  "
                    "4. Pass the right MAC address: hcitool lescan | grep Nuimo" % nuimo.macAddress)
                sys.exit()
            print("Connected. Waiting for input events...")
        self.clear_buffer()

    def set_pixel(self, x, y, state):
        if state:
            # set x'th character to be "*"
            self.buffer[y][x] = "*"
        else:
            # set x'th character to be a space " "
            self.buffer[y][x] = " "

    def get_next_char(self):
        if self.charGen.charCodeOrd >= 258:
            self.charGen.charCodeOrd = 1
        self.charGen.charCodeOrd += 1
        return self.charGen.get_matrix_string_ord(self.charGen.charCodeOrd)

    def get_previous_char(self):
        if self.charGen.charCodeOrd <= 0:
            self.charGen.charCodeOrd = 258
        self.charGen.charCodeOrd -= 1
        return self.charGen.get_matrix_string_ord(self.charGen.charCodeOrd)

    def next_char(self):
        if self.charGen.charCodeOrd >= 257:
            self.charGen.charCodeOrd = 1
        self.nuimo.display_led_matrix(self.charGen.get_matrix_string_ord(self.charGen.charCodeOrd + 1), 3.0)

    def previous_char(self):
        if self.charGen.charCodeOrd <= 0:
            self.charGen.charCodeOrd = 258
        self.nuimo.display_led_matrix(self.charGen.get_matrix_string_ord(self.charGen.charCodeOrd - 1), 3.0)

    def current_char(self):
        self.nuimo.display_led_matrix(self.charGen.get_matrix_string_ord(self.charGen.charCodeOrd), 3.0)

    def clear_buffer(self):
        self.buffer = [list('         ') for _ in range(9)]

    def write_buffer(self):
        data = ""
        print("---------")
        for row in self.buffer:
            print(''.join(row))
            data += ''.join(row)
        print("---------")
        if _platform != "darwin":
            try:
                self.nuimo.display_led_matrix(data, 1.0)
            except TypeError:
                return
        else:
            print("Can't send to Nuimo, running on OS X!")


class WorkerThread(QThread):
    def __init__(self, function, *args, **kwargs):
        QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    # def __del__(self):
    #    self.wait()

    def run(self):
        for i in xrange(sys.maxunicode):
          print unichr(i);
        self._result = None
        self._result = self.function(*self.args, **self.kwargs)
        return

    def result(self):
        return self._result


class MatrixWidget(QtGui.QWidget):
    def __init__(self):
        global scroll_worker

        super(MatrixWidget, self).__init__()

        font = QtGui.QFont()
        font.setPointSize(12)

        scroll_worker = WorkerThread(self.fn_scroll_worker)

        self.w = 29
        self.setGeometry(160, 160, 320, 400)
        self.setWindowTitle('Nuimo Matrix Tester')
        self.clear_pixel_buffer()
        self.setFixedSize(self.width(), self.height())
        self.leds = LedMatrix()

        # Send button
        self.pBSend = QtGui.QPushButton(self)
        self.pBSend.setGeometry(QtCore.QRect(105, 325, 110, 30))
        self.pBSend.setFont(font)
        self.pBSend.setObjectName(_fromUtf8("pBSend"))
        self.pBSend.setText("Send to Nuimo")
        self.pBSend.clicked.connect(self.on_send)

        # Right button
        self.pBRight = QtGui.QPushButton(self)
        self.pBRight.setGeometry(QtCore.QRect(225, 325, 30, 20))
        self.pBRight.setFont(font)
        self.pBRight.setObjectName(_fromUtf8("pBRight"))
        self.pBRight.setText(">")
        self.pBRight.clicked.connect(self.on_button_click_right)

        # Left button
        self.pBLeft = QtGui.QPushButton(self)
        self.pBLeft.setGeometry(QtCore.QRect(65, 325, 30, 20))
        self.pBLeft.setFont(font)
        self.pBLeft.setObjectName(_fromUtf8("pBLeft"))
        self.pBLeft.setText(""                  "<")
        self.pBLeft.clicked.connect(self.on_button_click_left)

        # textEdit field
        self.tEText = QtGui.QLineEdit(self)
        self.tEText.setGeometry(QtCore.QRect(65, 355, 185, 20))
        self.tEText.setFont(font)
        self.tEText.setObjectName(_fromUtf8("tEText"))
        self.tEText.setText(u"Попробуйте прокрутки текста...")

        # Start button
        self.pBStart = QtGui.QPushButton(self)
        self.pBStart.setGeometry(QtCore.QRect(105, 375, 110, 30))
        self.pBStart.setFont(font)
        self.pBStart.setObjectName(_fromUtf8("pBStart"))
        self.pBStart.setText("Scroll Text")
        self.pBStart.clicked.connect(self.on_button_click_start)

        # init buffer
        self.buffer = [list('         ') for _ in range(9)]

        # show ui
        self.show()

    def clear_pixel_buffer(self):
        self.buffer = [list('         ') for _ in range(9)]

    """ override QWidget.mousePressEvent(QMouseEvent) """
    def mousePressEvent(self, qt_mouse_event):
        x = qt_mouse_event.pos().x()
        y = qt_mouse_event.pos().y()
        x = x / self.w - 1
        y = y / self.w - 1
        if x <= -1 or y <= -1 or x >= 9 or y >= 9:
            self.clear_pixel_buffer()
            self.update()
            self.leds.clear_buffer()
            self.leds.write_buffer()
            return

        # if we get here the coords should be in range
        self.set_pixel(x, y, self.buffer[y][x] != "*")
        self.update()
        # show the hex representation
        result = ''
        for y in range(1, 9):
            bitstring = ''.join(self.buffer[y])[1: 9].replace(' ', '0').replace('*', '1')
            if str(hex(int(bitstring[1: 7], 2))).__len__() == 3:
                result += str(hex(int(bitstring, 2))).replace('x', 'x0') + ' '
            else:
                result += str(hex(int(bitstring, 2))) + ' '

        self.tEText.setText(result.upper().replace('X', 'x'))

    """ Overrides QWidget.paintEvent(QPaintEvent) """
    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.refresh(qp, ev)
        qp.end()

    def on_button_click_start(self):
        scroll_worker.start()

    def on_button_click_right(self):
        # paint on our qt-matrix
        char_matrix = self.leds.get_next_char()
        self.paint_display(char_matrix)
        self.tEText.setText("(not really)ASCII code:" + str(self.leds.charGen.charCodeOrd))
        # display on Nuimo
        if _platform != "darwin":
            self.leds.current_char()

    def on_button_click_left(self):
        # paint on our qt-matrix
        char_matrix = self.leds.get_previous_char()
        self.paint_display(char_matrix)
        self.tEText.setText("(not really)ASCII code:" + str(self.leds.charGen.charCodeOrd))
        # display on Nuimo
        if _platform != "darwin":
            self.leds.current_char()

    def fn_scroll_worker(self):
        """
        Function will update scrolling text every 0.3 seconds (endless loop)
        The function is executed in a Worker-Thread
        """
        text = self.tEText.text()
        codec = QtCore.QTextCodec.codecForName('utf-8')
        text = unicode(codec.fromUnicode(text), 'utf-8')


        # define the text buffer used for scrolling
        string_rep = ['' for _ in range(9)]
        length = 0
        # add a couple of spaces to clear display after scrolling
        text += '    '
        # build the buffer for fifo
        for i in text:
            matrix = self.leds.charGen.get_matrix(i)
            for idx, item in enumerate(matrix):
                if ord(i) == 32:
                    # reduce spacing
                    string_rep[idx] += matrix[idx].replace('0', ' ').replace('1', '*')[0:2]
                else:
                    string_rep[idx] += matrix[idx].replace('0', ' ').replace('1', '*')[0:8]
                length = string_rep[idx].__len__()

        # uncomment below to see a preview of the
        # banner to be scrolled in the output ;-)
        for i in string_rep:
            print(i)
            print('\033[2A')
        pos = 0
        interval = 0.05
        debug = False
        while True:
            try:
                if pos > length - 9:
                    print("Done scrolling..")
                    self.pBStart.setEnabled(True)
                    return
                else:
                    self.pBStart.setEnabled(False)
                # now let's roll
                matrix = ''
                # build matrix from rep
                for i in string_rep:
                    matrix += i[pos:pos+9]
                    # scroll in terminal window
                    if debug:
                        print(i[pos:pos+9].replace('*', '1').replace(' ', '*').replace('1', ' '))
                if debug:
                    print('\033[10A')
                # display on ui
                self.paint_display(matrix)

                # send to Nuimo
                if _platform != "darwin":
                    self.leds.nuimo.display_led_matrix(matrix, 3.0)

                pos += 1
                time.sleep(interval)
            except Exception as e:
                print(e.message)
                return

    def paint_display(self, char_matrix):
        for y in range(9):
            for x in range(9):
                start = (y * 9) + x
                state = (char_matrix[start:start + 1] == "*")
                self.set_pixel(x, y, state)
        self.update()

    def set_pixel(self, x, y, state):
        if state:
            self.leds.set_pixel(x, y, True)
            self.buffer[y][x] = "*"
        else:
            self.leds.set_pixel(x, y, False)
            self.buffer[y][x] = " "

    def draw_led(self, qp, x, y):
        state = (self.buffer[y][x] == "*")
        if state:
            col = QtGui.QColor("#FFFFFF")  # white
        else:
            col = QtGui.QColor("#333333")  # grey
        qp.setPen(col)
        qp.setBrush(col)
        qp.drawEllipse(self.w + self.w * x, self.w + self.w * y, self.w - 3, self.w - 3)

    def refresh(self, qp, event):
        qp.setBrush(QtCore.Qt.black)
        qp.drawRect(event.rect())
        for y in range(9):
            for x in range(9):
                self.draw_led(qp, x, y)

    def on_send(self):
        self.leds.write_buffer()
        return


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = MatrixWidget()
    sys.exit(app.exec_())
