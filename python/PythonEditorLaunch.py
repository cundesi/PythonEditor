#!/net/homes/mlast/bin nuke-safe-python-tg
""" Launch PythonEditor as a Standalone Application.
This file can also be executed from within an existing
Qt QApplication to launch PythonEditor in a separate window.
"""
from __future__ import absolute_import
import sys
import os
import time

sys.dont_write_bytecode = True
start = time.time()

os.environ['PYTHONEDITOR_CAPTURE_STARTUP_STREAMS'] = '1'

# with startup variables set,
# we can now import the package in earnest.
from PythonEditor.ui import ide
from PythonEditor.ui.features import ui_palette
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.Qt import QtGui
from PythonEditor.ui.Qt import QtCore


def main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    PDF = 'PYTHONEDITOR_DEFAULT_FONT'
    os.environ[PDF] = 'Source Code Pro for Powerline'
    _ide = ide.IDE()
    _ide.setParent(app.activeWindow())
    _ide.setWindowFlags(QtCore.Qt.Window)
    _ide.setPalette(ui_palette.get_palette_style())

    # Plastique isn't available on Windows, so try multiple styles.
    styles = QtWidgets.QStyleFactory.keys()
    style_found = False
    for style_name in ['Plastique', 'Fusion']:
        if style_name in styles:
            print('Setting style to:', style_name)
            style_found = True
            break

    if style_found:
        style = QtWidgets.QStyleFactory.create(style_name)
        _ide.setStyle(style)

    print('PythonEditor import time: %.04f seconds' % (time.time() - start))
    _ide.showMaximized()
    if app.applicationName() in ['python', 'mayapy']:
        sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except:
        import traceback
        traceback.print_exc()
