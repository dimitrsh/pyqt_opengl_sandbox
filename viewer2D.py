from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import Qt
import sys

from scene2d import Scene2D

class Viewer2D(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('2D-viewer')
        #self.setWindowIcon(QtGui.QIcon(os.path.join(CUR_DIR, KVAZAR_ICON)))
        self.resize(800, 600)
        self.opengl_window = Scene2D(self)
        self.opengl_window.resize(800, 600)
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.opengl_window)
        self.setLayout(mainLayout)

if __name__ == '__main__':    
    app = QtGui.QApplication(sys.argv)
    won = Viewer2D()
    
    won.show()

    sys.exit(app.exec_())
