from PySide6 import QtGui
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QFontDatabase
from PySide6.QtCore import Qt, QRegularExpression

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._initialize_formats()
        self._setup_rules()

    def _initialize_formats(self):
        # Initialize formats for different syntax elements
        self.formats = {}

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#800080"))  # dark purrple
        keyword_format.setFontWeight(QFont.Bold)
        self.formats['keyword'] = keyword_format

        # Built-ins and special constants
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#B8860B"))  # dark yellow
        self.formats['builtin'] = builtin_format

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)
        self.formats['comment'] = comment_format

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#800000"))  # Maroon
        self.formats['string'] = string_format

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF00FF"))  # Magenta
        self.formats['number'] = number_format

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#B000B0"))  # Purple
        self.formats['operator'] = operator_format

        # Braces
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor("#FFFFFF"))  # White
        self.formats['brace'] = brace_format

    def _setup_rules(self):
        # Regular expressions for syntax elements
        self.rules = []

        # Keywords
        keywords = [
            'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        keyword_patterns = [r'\b{}\b'.format(word) for word in keywords]
        for pattern in keyword_patterns:
            self.rules.append((QRegularExpression(pattern), self.formats['keyword']))

        # Built-in functions and constants
        builtins = [
            'abs', 'dict', 'help', 'min', 'setattr', 'all', 'dir', 'hex', 'next', 'slice',
            'any', 'divmod', 'id', 'object', 'sorted', 'ascii', 'enumerate', 'input', 'oct', 'staticmethod',
            'bin', 'eval', 'int', 'open', 'str', 'bool', 'exec', 'isinstance', 'ord', 'sum',
            'bytearray', 'filter', 'issubclass', 'pow', 'super', 'bytes', 'float', 'iter', 'print', 'tuple',
            'callable', 'format', 'len', 'property', 'type', 'chr', 'frozenset', 'list', 'range', 'vars',
            'classmethod', 'getattr', 'locals', 'repr', 'zip', 'compile', 'globals', 'map', 'reversed', '__import__',
            'complex', 'hasattr', 'max', 'round', 'delattr', 'hash', 'memoryview', 'set', 'setattr',
            'Ellipsis', 'NotImplemented', '__debug__'
        ]
        builtin_patterns = [r'\b{}\b'.format(word) for word in builtins]
        for pattern in builtin_patterns:
            self.rules.append((QRegularExpression(pattern), self.formats['builtin']))

        # Comments
        self.rules.append((QRegularExpression(r'#.*'), self.formats['comment']))

        # Strings (single and double quotes)
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats['string']))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.formats['string']))

        # Numbers
        self.rules.append((QRegularExpression(r'\b[+-]?[0-9]+[lL]?\b'), self.formats['number']))
        self.rules.append((QRegularExpression(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b'), self.formats['number']))
        self.rules.append((QRegularExpression(r'\b[+-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?\b'), self.formats['number']))

        # Operators
        operators = [
            '=', '==', '!=', '<', '<=', '>', '>=',
            r'\+', '-', r'\*', '/', '//', '%', r'\*\*',
            r'\+=', '-=', r'\*=', '/=', '%=', '^=', '&=', r'\|=', '>>=', '<<=',
            '\^', r'\\|', '&', '~', '>>', '<<'
        ]
        operator_patterns = [r'{}'.format(op) for op in operators]
        for pattern in operator_patterns:
            self.rules.append((QRegularExpression(pattern), self.formats['operator']))

        # Braces
        braces = [r'\{', r'\}', r'\(', r'\)', r'\[', r'\]']
        for brace in braces:
            self.rules.append((QRegularExpression(brace), self.formats['brace']))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            expression = pattern.globalMatch(text)
            while expression.hasNext():
                match = expression.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)

        self.setCurrentBlockState(0)

        # Multiline strings (''' or """)
        in_multiline = self.match_multiline(text, r"'''", self.formats['string'])
        if not in_multiline:
            self.match_multiline(text, r'"""', self.formats['string'])

    def match_multiline(self, text, delimiter, fmt):
        start_delim = QRegularExpression(delimiter)
        end_delim = QRegularExpression(delimiter)
        if self.previousBlockState() == 1:
            start = 0
            add = 0
        else:
            match = start_delim.match(text)
            start = match.capturedStart()
            add = match.capturedLength()

        while start >= 0:
            match = end_delim.match(text, start + add)
            if match.hasMatch():
                end = match.capturedEnd()
                length = end - start
                self.setFormat(start, length, fmt)
                start = start_delim.match(text, end).capturedStart()
            else:
                self.setCurrentBlockState(1)
                length = len(text) - start
                self.setFormat(start, length, fmt)
                return True
        return False

class CodeWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        self.setFont(font)
        self.highlighter = PythonSyntaxHighlighter(self.document())
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
