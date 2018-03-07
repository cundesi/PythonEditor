import os
import sys
import re
import time
print 'importing', __name__, 'at', time.asctime()
user = os.environ.get('USERNAME')

print sys.version
print sys.executable

try:
    import nuke
except ImportError:
    pass
    
from qt import QtGui, QtCore

from features import syntaxhighlighter

class CodeEditor(QtGui.QPlainTextEdit):
    clearOutput = QtCore.Signal()

    def __init__(self, file, output):
        super(CodeEditor, self).__init__()
        self._globals = dict()
        self._locals = dict()
        self._file = file

        self.clearOutput.connect(output.clear)

        syntaxhighlighter.Highlight(self.document())

        if not True: #temp disable stylesheet for development
            self.setStyleSheet('background:#282828;color:#EEE;') # Main Colors
            self.font = QtGui.QFont()
            self.font.setFamily("Courier")
            self.font.setStyleHint(QtGui.QFont.Monospace)
            self.font.setFixedPitch(True)
            self.font.setPointSize(8)
            self.setFont(self.font)
            self.setTabStopWidth(4 * QtGui.QFontMetrics(self.font).width(' '))

        self.setTabStopWidth(4 * QtGui.QFontMetrics(self.font()).width(' '))

    def showEvent(self, event):
        try:
            self.setup_env()
        except:
            self._globals = globals()
            self._locals = locals()
        super(CodeEditor, self).showEvent(event)

    def setup_env(self):
        nuke.tcl('python -exec "SublimeNuke.editor.base._globals = globals()"')
        nuke.tcl('python -exec "SublimeNuke.editor.base._locals = locals()"')

        self._globals = _globals
        self._locals = _locals
        self._locals.update({'__instance':self})#this will only refer to the latest instance; not sure how useful that is.

    def keyReleaseEvent(self, event):
        """
        File edit commits happen on keyRelease.
        """

        with open(self._file, 'w') as f:
            f.write(self.toPlainText())

        super(CodeEditor, self).keyReleaseEvent(event)
        
    def keyPressEvent(self, event):
        """
        What happens when keys are pressed.
        """
        if event.key() in (QtCore.Qt.Key_Return,
                           QtCore.Qt.Key_Enter):
            print 'enter'
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.begin_exec()

            elif event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier:
                textCursor = self.textCursor()
                line = textCursor.block().text()
                indentCount = len(line) - len(line.lstrip(' '))
                textCursor.movePosition(textCursor.StartOfLine)
                self.setTextCursor(textCursor)
                textCursor.insertText(' '*indentCount+'\n')
                self.moveCursor(textCursor.Left)
                return True
            else:
                textCursor = self.textCursor()
                line = textCursor.block().text()
                indentCount = len(line) - len(line.lstrip(' '))
                textCursor.insertText('\n'+' '*indentCount)
                return True

        if event.key() in (QtCore.Qt.Key_Backspace,):
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.clearOutput.emit()
                return True

        if event.key() == QtCore.Qt.Key_Tab:
            textCursor = self.textCursor()
            textCursor.insertText('    ')
            return True

        if (event.key() == QtCore.Qt.Key_Slash
                and event.modifiers() == QtCore.Qt.ControlModifier):
            textCursor = self.textCursor()
            text = textCursor.selection()#.toPlainText()
            print text
            raise NotImplementedError, 'add comment code toggle here'
            # block = textCursor.block()
            # print block
            # line = textCursor.block().text()
            # print line
            # textCursor.movePosition(textCursor.StartOfLine)
            # self.setTextCursor(textCursor)
            # if (not line.lstrip().startswith('#')
                    # or line.strip() == ''):
                # textCursor.insertText('#')
            # else:
                # textCursor.deletePreviousChar()
            # self.moveCursor(textCursor.Left)
            return True

        if (event.key() == QtCore.Qt.Key_BracketRight
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add right indent here'

        if (event.key() == QtCore.Qt.Key_BracketLeft
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add left indent here'

        if (event.key() == QtCore.Qt.Key_K
            and event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add delete line'

        # keyDict = {value:key for key, value in QtCore.Qt.__dict__.iteritems()}
        # print keyDict.get(event.key()), event.text()

        super(CodeEditor, self).keyPressEvent(event)

    #code execution
    def begin_exec(self):
        textCursor = self.textCursor()
        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()
            if 'nuke' in self._globals.keys():
                self.node_context_exec(text)
            else:
                self.global_exec(text)
        else:
            text = self.toPlainText()
            if 'nuke' in self._globals.keys():
                self.node_context_exec(text)
            else:
                self.global_exec(text)

    def get_node_context(self):
        """
        Use nuke's node stack to 
        determine current node context group.
        Root (top level) by default.
        """
        group = 'root' if not hasattr(self, 'node_context') else self.node_context
        stack = nuke.tcl('stack')
        if stack:
            stack_list = stack.split(' ')
            for item in stack_list:
                if 'node' in item:
                    node = nuke.toNode(item)
                    if not isinstance(node, nuke.PanelNode):
                        node_path = node.fullName()
                        group = 'root' if not '.' in node_path else '.'.join( ['root'] + node_path.split('.')[:-1] )
                        print group
                        return group
        return group

    def node_context_exec(self, text):
        self.node_context = self.get_node_context()
        nuke.toNode(self.node_context).begin()
        self.global_exec(text)
        nuke.toNode(self.node_context).end()
        
    def global_exec(self, text):
        #get context
        local = self._locals.copy()
        single = len(text.rstrip().lstrip().split(' ')) == 1
        if single:
            code = compile(text, '<i.d.e>', 'single')
        else:
            code = compile(text, '<i.d.e>', 'exec')

        self.exec_text(code)

        # new_locals = {k:self._locals[k] for k in set(self._locals) - set(local)}
        new_locals = dict()
        for k in set(self._locals) - set(local):
            new_locals[k] = self._locals[k]
        
        if new_locals and 'import' in text: 
            print new_locals # this should only happen in compile(text, '<string>', 'single') mode

    def exec_text(self, text):
        print '# Result:'
        exec(text, self._globals, self._locals)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        self.node_context = self.get_node_context()
        with nuke.toNode(self.node_context):
            pythonknobs = [k for k in nuke.selectedNode().allKnobs()
                            if type(k) in (nuke.PyScript_Knob,
                                          nuke.PythonKnob)]
            for knob in pythonknobs:
                menu.addAction('Load {0}'.format(knob.name()), lambda k=knob: nuke.message(k.value()))


        menu.exec_(QtGui.QCursor().pos())

    # -------------------------------------------------------------------------------
    #shortcuts
    # -------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    app.exec_()