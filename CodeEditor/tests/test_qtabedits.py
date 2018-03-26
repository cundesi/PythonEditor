import sys
import os

TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )
TEST_FILE = os.path.join( PACKAGE_PATH, 'tests/test_code.py')

with open( TEST_FILE, 'r' ) as f:
    TEST_CODE = f.read()

for m in sys.modules.keys():
    if 'codeeditor' in m:
        del sys.modules[m]

from codeeditor.ui.Qt import QtWidgets, QtGui, QtCore
from codeeditor.ui import edittabs 

@QtCore.Slot(int)
def cw(num):
    print num

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    app = QtWidgets.QApplication(sys.argv)
    tabs = edittabs.EditTabs()
    # tabs.currentChanged.connect(cw)
    # tabs.tabCloseRequested.connect(cw)
    tabs.show()
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())
