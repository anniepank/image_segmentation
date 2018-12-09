#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLabel, QVBoxLayout, QGroupBox, QRadioButton, QPushButton, QSizePolicy, QPlainTextEdit, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QPolygon, QImage, QFont
from PyQt5.QtCore import Qt
from skimage.segmentation import random_walker
import matplotlib.image as mpimg
from PIL import Image
from PIL.ImageQt import ImageQt
from fpdf import FPDF, HTMLMixin
import matplotlib.pyplot as plt
import platform
import numpy as np
import signal
import os
import subprocess

UPLOAD_IMAGE_LEFT_OFFSET = 100
UPLOAD_IMAGE_TOP_OFFSET = 100
UPLOAD_IMAGE_WIDTH = 200
UPLOAD_IMAGE_HEGHT = 200
signal.signal(signal.SIGINT, signal.SIG_DFL)


class HTML2PDF(FPDF, HTMLMixin):
    pass

class UploadedImage(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, e):
        QLabel.paintEvent(self, e)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        for color in [Qt.red, Qt.blue, Qt.green]:
            pen = QPen(color, 5)
            brush = QBrush(color)
            qp.setPen(pen)
            qp.setBrush(brush)
            for point in self.points:
                qp.drawPoints(QPolygon([x['point'] for x in self.points if x['color'] == color]))

class MainWindowWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()


    def create_pdf(self, event):
        pdf = FPDF()
        pdf.add_page()
        header='Random walker'
        pdf.set_font("Arial", size=24)
        pdf.cell(0,10, txt=header, ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0,10, txt=self.name.text(), ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0,10, txt="Images: initial and segmented", ln=1, align="L")

        if os.path.exists(self.initial_image_url):
            pdf.image(self.initial_image_url, x=10, y=47, w=45)

        if os.path.exists('segmented.png'):
            pdf.image("segmented.png", x=10, y=100, w=45)
        pdf.cell(0, 120, ln=1)
        pdf.cell(1,10, txt="Code:", ln=1, align="L")
        for l in self.codeSegment.toPlainText().splitlines():
            pdf.cell(0,5, txt=l, ln=1, align="L")
        try:
            pdf.output('assigment.pdf')
            if sys.platform == 'linux':
                subprocess.call(['xdg-open', 'assigment.pdf'])
            if sys.platform == 'win32':
                subprocess.call(['start', 'assigment.pdf'])

        except Exception:
            import traceback
            tb = traceback.format_exc()
            self.output.insertPlainText(tb + '\n')

    def initUI(self):
        self.resize(1200, 900)
        self.setWindowTitle('Random Walker assigment')

        self.name = QLineEdit(self)
        self.name.move(20, 20)
        self.name.resize(280,40)
        self.name.setText('Your name, surname, course and group number')

        self.uploadedImage = UploadedImage(self)
        self.uploadedImage.setGeometry(UPLOAD_IMAGE_LEFT_OFFSET, UPLOAD_IMAGE_TOP_OFFSET, UPLOAD_IMAGE_WIDTH, UPLOAD_IMAGE_HEGHT)
        self.uploadedImage.mousePressEvent = self.addMarker
        self.uploadedImage.setScaledContents(True)
        self.uploadedImage.setFixedWidth(200)

        self.segmentedImage = QLabel(self)
        self.segmentedImage.setGeometry(UPLOAD_IMAGE_WIDTH + 150, 100, 200, 200)
        self.segmentedImage.setScaledContents(True)
        self.segmentedImage.setFixedWidth(200)

        self.studentImage = QLabel(self)
        self.studentImage.setGeometry(UPLOAD_IMAGE_WIDTH + 150 + 300, 100, 200, 200)
        self.studentImage.setScaledContents(True)
        self.studentImage.setFixedWidth(200)


        groupBox = QGroupBox("Color", self)
        radio1 = QRadioButton("Red")
        radio2 = QRadioButton("Blue")
        radio3 = QRadioButton("Green")
        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        groupBox.move(100, 500)

        radio1.toggled.connect(self.radio1Clicked)
        radio2.toggled.connect(self.radio2Clicked)
        radio3.toggled.connect(self.radio3Clicked)

        self.codeSegment = QPlainTextEdit(self)
        initial_code = '#you code goes here. \n#Save your segmented image as \'segmented.png\'. \n#And you have two matricies available. \n#They are called: markers and image'
        self.codeSegment.insertPlainText(initial_code)
        self.code = initial_code
        self.codeSegment.resize(400, 300)

        f = QFont("unexistent")
        f.setStyleHint(QFont.Monospace)
        self.codeSegment.setFont(f)

        self.output = QPlainTextEdit(self)
        self.output.resize(200, 300)
        self.output.setReadOnly(True)
        self.output.setFont(f)

        self.runButton = QPushButton('Run', self)
        self.runButton.clicked.connect(self.runCode)

        button = QPushButton('Segment', self)
        button.clicked.connect(self.segment)

        reset = QPushButton('Reset', self)
        reset.clicked.connect(self.reset)

        pdfButton = QPushButton('Create PDF', self)
        pdfButton.clicked.connect(self.create_pdf)

        self.points = self.uploadedImage.points = []
        self.color = Qt.red

        self.initial_image_url = '/home/anya/Documents/Kursach/images.png'
        self.setImage(self.initial_image_url)

        hbox = QHBoxLayout()
        hbox.addSpacing(30)
        hbox.addWidget(self.uploadedImage)
        hbox.addStretch(1)
        hbox.addWidget(self.segmentedImage)
        hbox.addStretch(1)
        hbox.addWidget(self.studentImage)
        hbox.addSpacing(30)

        hbox2 = QHBoxLayout()
        hbox2.addSpacing(30)
        hbox2.addWidget(groupBox)
        hbox2.addSpacing(50)
        hbox2.addWidget(self.codeSegment)
        hbox2.addSpacing(30)
        hbox2.addWidget(self.output)
        hbox2.addSpacing(30)

        hbox3 = QHBoxLayout()
        hbox3.addSpacing(30)
        hbox3.addWidget(button)
        hbox3.addWidget(reset)
        hbox3.addWidget(self.runButton)
        hbox3.addSpacing(270)
        hbox3.addWidget(pdfButton)
        hbox3.addSpacing(30)

        fixed = QWidget()
        fixed.setLayout(hbox)
        fixed.setFixedHeight(230)

        vbox = QVBoxLayout()
        vbox.addSpacing(20)
        vbox.addWidget(self.name)
        vbox.addWidget(fixed,0)
        vbox.addSpacing(20)
        vbox.addLayout(hbox2,1)
        vbox.addSpacing(20)
        vbox.addLayout(hbox3,0)
        vbox.addSpacing(20)

        self.setLayout(vbox)

        self.show()

    def runCode(self, e):
        self.code = self.codeSegment.toPlainText()
        def myprint(*args):
            self.output.insertPlainText(' '.join(str(a) for a in args) + '\n')

        code_object = compile(self.code, '<string>', 'exec')

        try:
            builtins = dict(__builtins__.__dict__)
            builtins['print'] = myprint
            exec(code_object, {
                '__builtins__': builtins,
                'image': self.convertImageToArray(),
                'markers': self.markers,
                # remove imports
                'random_walker': random_walker,
                'np': np,
                'Image': Image,
                'QPixmap': QPixmap
            })
        except Exception:
            import traceback
            tb = traceback.format_exc()
            self.output.insertPlainText(tb + '\n')

        if os.path.exists('segmented.png'):
            with open('segmented.png') as img:
                pixmap = QPixmap('segmented.png')
                self.studentImage.setPixmap(pixmap)


    def reset(self, e):
        self.markers = np.zeros_like(self.convertImageToArray())
        self.points = self.uploadedImage.points = []
        self.uploadedImage.update()

    def segment(self, e):
        data = self.convertImageToArray()
        result = random_walker(data, self.markers, beta=10, mode='bf')

        result = np.asarray([[x*100  for x in row] for row in result]).astype('uint8')
        img = Image.fromarray(result, 'L')
        img.save('segmented_by_program.png')
        self.segmentedImage.setPixmap(QPixmap.fromImage(ImageQt(img )))

    def radio1Clicked(self, e):
        self.color = Qt.red

    def radio2Clicked(self, e):
        self.color = Qt.blue

    def radio3Clicked(self, e):
        self.color = Qt.green

    def addMarker(self, e):
        point = e.pos()

        color = {
            Qt.red: 1,
            Qt.blue: 2,
            Qt.green: 3
        }[self.color]

        x, y = point.x(), point.y()
        scaleX = self.uploadedImage.geometry().width() / self.imageData.shape[1]
        scaleY = self.uploadedImage.geometry().height() / self.imageData.shape[0]

        x /= scaleX
        y /= scaleY

        y = min(max(0, y), self.imageData.shape[0] - 1)
        x = min(max(0, x), self.imageData.shape[1] - 1)
        print('x: ', x, 'y: ', y)
        self.markers[int(y), int(x)] = color

        point.setX(point.x())
        point.setY(point.y())

        self.points.append({'point': e.pos(), 'color': self.color})
        self.uploadedImage.update()

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        url = e.mimeData().urls()[0].toLocalFile()
        self.initial_image_url = url
        print(url)
        self.setImage(url)

    def setImage(self, url):
        pixmap = QPixmap(url)
        self.imageData = mpimg.imread(url)
        self.uploadedImage.setPixmap(pixmap)

        self.uploadedImage.setScaledContents(True)
        self.markers = np.zeros_like(self.convertImageToArray())

    def convertImageToArray(self):
        if type(self.imageData[0][0]) is np.float32:
            return self.imageData
        return np.asarray([
            [sum(pixel) / 3 for pixel in row]
            for row in self.imageData
        ])

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindowWidget()
    sys.exit(app.exec_())


"""
result = random_walker(image, markers, beta=10, mode='bf')

result = np.asarray([[x*100  for x in row] for row in result]).astype('uint8')
img = Image.fromarray(result, 'L')
img.save('segmented_by_program.png')
"""

#pyinstaller application.py --hidden-import=pywt._extensions._cwt
