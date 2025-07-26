# # syntax_highlighter.py

# import re
# from PyQt6.QtCore import Qt
# from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

# class Highlighter(QSyntaxHighlighter):
#     def __init__(self, parent, language='python'):
#         super().__init__(parent)
#         self.highlighting_rules = []
        
#         # --- Định nghĩa các định dạng (màu sắc, kiểu chữ) ---
#         keyword_format = QTextCharFormat()
#         keyword_format.setForeground(QColor("#569CD6")) # Màu xanh dương cho từ khóa
#         keyword_format.setFontWeight(QFont.Weight.Bold)

#         string_format = QTextCharFormat()
#         string_format.setForeground(QColor("#CE9178")) # Màu cam cho chuỗi

#         comment_format = QTextCharFormat()
#         comment_format.setForeground(QColor("#6A9955")) # Màu xanh lá cho bình luận
#         comment_format.setFontItalic(True)
        
#         number_format = QTextCharFormat()
#         number_format.setForeground(QColor("#B5CEA8")) # Màu xanh nhạt cho số

#         operator_format = QTextCharFormat()
#         operator_format.setForeground(QColor("#D4D4D4")) # Màu trắng xám cho toán tử

#         # --- Định nghĩa các bộ từ khóa cho mỗi ngôn ngữ ---
#         python_keywords = [
#             'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
#             'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
#             'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not',
#             'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
#         ]
        
#         c_java_keywords = [
#             'char', 'class', 'const', 'double', 'else', 'enum', 'float', 'for',
#             'if', 'int', 'long', 'private', 'protected', 'public', 'return',
#             'short', 'static', 'struct', 'switch', 'void', 'while', 'true', 'false',
#             'new', 'import', 'package', 'final', 'extends', 'implements', 'throws'
#         ]

#         # --- Tạo quy tắc tô màu dựa trên ngôn ngữ được chọn ---
#         if language == 'python':
#             keywords = python_keywords
#             # Quy tắc cho Python
#             self.highlighting_rules.extend([(f'\\b{word}\\b', keyword_format) for word in keywords])
#             self.highlighting_rules.append(('[_a-zA-Z][_a-zA-Z0-9]*(?=\\()', QTextCharFormat())) # Tô màu hàm (tạm thời để màu mặc định)
#             self.highlighting_rules.append(('#[^\n]*', comment_format)) # Bình luận
#             self.highlighting_rules.append(('"([^"\\\\\n]|\\\\.)*"', string_format)) # Chuỗi trong ""
#             self.highlighting_rules.append(("_`([^'`\\\\\n]|\\\\.)*`_", string_format)) # Chuỗi trong ''
        
#         elif language in ['c', 'java']:
#             keywords = c_java_keywords
#             # Quy tắc chung cho C/Java
#             self.highlighting_rules.extend([(f'\\b{word}\\b', keyword_format) for word in keywords])
#             self.highlighting_rules.append(('"([^"\\\\\n]|\\\\.)*"', string_format)) # Chuỗi
            
#             # Xử lý bình luận nhiều dòng cho C/Java
#             self.multi_line_comment_format = comment_format
#             self.comment_start_expression = re.compile(r'/\*')
#             self.comment_end_expression = re.compile(r'\*/')

#             # Bình luận một dòng
#             self.highlighting_rules.append(('//[^\n]*', comment_format))

#         # Quy tắc chung cho tất cả
#         self.highlighting_rules.append(('\\b[0-9]+\\.?[0-9]*\\b', number_format)) # Số
#         self.highlighting_rules.append(('[+\\-*<>=!&|;^%~,./?:]', operator_format)) # Toán tử
        
#     def highlightBlock(self, text):
#         # Áp dụng các quy tắc tô màu cho từng dòng
#         for pattern, format in self.highlighting_rules:
#             for match in re.finditer(pattern, text):
#                 self.setFormat(match.start(), match.end() - match.start(), format)

#         self.setCurrentBlockState(0)

#         # Xử lý bình luận nhiều dòng (chỉ dành cho C/Java)
#         if hasattr(self, 'comment_start_expression'):
#             start_index = 0
#             if self.previousBlockState() != 1:
#                 match = self.comment_start_expression.search(text)
#                 if match:
#                     start_index = match.start()

#             while start_index >= 0:
#                 match = self.comment_end_expression.search(text, start_index)
#                 if not match:
#                     self.setCurrentBlockState(1)
#                     comment_length = len(text) - start_index
#                 else:
#                     comment_length = match.start() - start_index + match.end() - match.start()
                
#                 self.setFormat(start_index, comment_length, self.multi_line_comment_format)
                
#                 match = self.comment_start_expression.search(text, start_index + comment_length)
#                 start_index = match.start() if match else -1

import sys
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent, language='python'):
        super().__init__(parent)
        self.highlighting_rules = []

        # --- Định nghĩa các định dạng (màu sắc, kiểu chữ) ---
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6")) # Xanh dương
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#C586C0")) # Tím
        preprocessor_format.setFontWeight(QFont.Weight.Bold)

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955")) # Xanh lá
        comment_format.setFontItalic(True)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178")) # Cam

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8")) # Xanh nhạt

        # --- Định nghĩa từ khóa và quy tắc cho từng ngôn ngữ ---

        # --- QUY TẮC CHO C/C++ ---
        if language in ['c', 'cpp']:
            c_cpp_keywords = [
                "auto", "break", "case", "char", "const", "continue", "default", "do",
                "double", "else", "enum", "extern", "float", "for", "goto", "if",
                "int", "long", "register", "return", "short", "signed", "sizeof", "static",
                "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
                "asm", "dynamic_cast", "namespace", "reinterpret_cast", "try", "bool",
                "explicit", "new", "static_cast", "typeid", "catch", "false", "operator",
                "template", "typename", "class", "friend", "private", "this", "using",
                "throw", "true", "public", "protected", "virtual", "delete", "inline"
            ]
            self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in c_cpp_keywords]
            
            # Chỉ thị tiền xử lý (#include, #define, ...)
            self.highlighting_rules.append((QRegularExpression("^#[a-zA-Z]+"), preprocessor_format))

        # --- QUY TẮC CHO JAVA ---
        elif language == 'java':
            java_keywords = [
                "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
                "class", "const", "continue", "default", "do", "double", "else", "enum",
                "extends", "final", "finally", "float", "for", "goto", "if", "implements",
                "import", "instanceof", "int", "interface", "long", "native", "new",
                "package", "private", "protected", "public", "return", "short", "static",
                "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
                "transient", "try", "void", "volatile", "while", "true", "false", "null"
            ]
            self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in java_keywords]
            
        # --- QUY TẮC CHO PYTHON (Giữ nguyên) ---
        elif language == 'python':
            python_keywords = [
                "and", "as", "assert", "break", "class", "continue", "def", "del",
                "elif", "else", "except", "False", "finally", "for", "from", "global",
                "if", "import", "in", "is", "lambda", "None", "nonlocal", "not",
                "or", "pass", "raise", "return", "True", "try", "while", "with", "yield"
            ]
            self.highlighting_rules += [(QRegularExpression(f"\\b{keyword}\\b"), keyword_format) for keyword in python_keywords]
        
        # --- CÁC QUY TẮC CHUNG CHO CÁC NGÔN NGỮ ---
        # Chuỗi ký tự trong dấu ngoặc kép ""
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        # Số
        self.highlighting_rules.append((QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"), number_format))
        # Chú thích đơn dòng (// cho C/Java, # cho Python)
        if language in ['c', 'cpp', 'java']:
            self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        if language == 'python':
            self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))
        
        # --- Xử lý chú thích đa dòng cho C/Java ---
        self.multi_line_comment_format = QTextCharFormat()
        self.multi_line_comment_format.setForeground(QColor("#6A9955")) # Xanh lá
        self.multi_line_comment_format.setFontItalic(True)

        self.comment_start_expression = QRegularExpression("/\\*")
        self.comment_end_expression = QRegularExpression("\\*/")


    def highlightBlock(self, text):
        # Áp dụng các quy tắc tô màu cơ bản (từ khóa, chuỗi, số, comment đơn dòng)
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        self.setCurrentBlockState(0)

        # Xử lý tô màu cho comment đa dòng (/* ... */)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start_expression.match(text)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart() if match.hasMatch() else -1
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
            
            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            
            match = self.comment_start_expression.match(text, start_index + comment_length)
            start_index = match.capturedStart() if match.hasMatch() else -1