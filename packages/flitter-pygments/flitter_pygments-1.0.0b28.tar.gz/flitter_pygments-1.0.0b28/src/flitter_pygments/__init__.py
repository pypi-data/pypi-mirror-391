"""
A Pygments lexer for the Flitter visuals functional programming language

https://flitter.readthedocs.io/
"""

from pygments.lexer import RegexLexer, include
from pygments.token import Keyword, Whitespace, Comment, Name, Literal, Operator, Punctuation


class FlitterLexer(RegexLexer):
    name = "Pygments Plugin Flitter Language"
    aliases = ["flitter", "flitter-lang"]
    filenames = ["*.fl"]
    mimetypes = ["text/x-flitter-lang"]

    builtin = ('beat', 'quantum', 'tempo', 'fps', 'delta', 'time', 'frame', 'performance', 'slow_frame', 'clock',
               'realtime', 'screen', 'fullscreen', 'vsync', 'offscreen', 'opengles', 'run_time')

    tokens = {
        'root': [
            (r'\A#!.*!', Comment.Hashbang),
            include('common'),
            (r'%pragma\b', Keyword.Reserved),
            (r'%include\b', Keyword.Reserved),
            (r'\b(for|in|import|from|if|elif|else|let|stable)\b', Keyword.Reserved),
            (r'\bfunc\b', Keyword.Declaration),
            (r"\!\w+'*(?![\w'])", Name.Tag, 'node'),
            (r"@\w+'*(?![\w'])", Name.Tag.Psuedo, 'node'),
            include('expressions'),
        ],

        'common': [
            (r'\\\n', Punctuation),
            (r'\s+', Whitespace),
            (r'--.*$', Comment.Single),

            # These characters are not part of the language, but are used in the documentation:
            (r'[《》…]', Comment.Special),
        ],

        'expressions': [
            (r'\b([0-9]+:)?[0-5]?[0-9]:[0-5]?[0-9](\.[0-9]+)?\b', Literal.Number.Time),
            (r'\b[-+]?([0-9][_0-9]*(\.[0-9][_0-9]*)?|\.[0-9][_0-9]*)([eE][-+]?[0-9][_0-9]*)?[pnuµmkMGT]?\b', Literal.Number),
            (r":\w+'*(?![\w'])", Literal.String.Symbol),
            (r'\b(for|in|where|if|else)\b', Keyword.Reserved),
            (r'\b(true|false|null|nan|inf)\b', Keyword.Constant),
            (r"\b({})(?!')\b".format('|'.join(builtin)), Name.Builtin),
            (r'(\.\.|//|\*\*|==|\!=|\<=|\>=|[-|+*/%<>\$=;])', Operator),
            (r'\b(and|or|xor|not)\b', Operator.Word),
            (r"(?<!\!#@:)\w+'*(?![\w'])", Name.Variable),
            (r'[(),\[\]]', Punctuation),
            (r'"""', Literal.String.Double, 'tdqs'),
            (r"(?<!\w)'''", Literal.String.Single, 'tsqs'),
            (r'"', Literal.String.Double, 'dqs'),
            (r"(?<!\w)'", Literal.String.Single, 'sqs'),
        ],

        'node': [
            (r'(?<!\\)\n', Whitespace, '#pop'),
            include('common'),
            (r"\b\w+'*\s*=(?!=)", Name.Attribute),
            (r"#\w+'*(?![\w'])", Name.Label),
            include('expressions'),
        ],

        'tdqs': [
            (r'"""', Literal.String.Double, '#pop'),
            (r'.', Literal.String.Double),
        ],

        'tsqs': [
            (r"'''", Literal.String.Single, '#pop'),
            (r'.', Literal.String.Single),
        ],

        'dqs': [
            (r'"', Literal.String.Double, '#pop'),
            (r'\\"', Literal.String.Escape),
            (r'[^\\\n"]*', Literal.String.Double),
        ],

        'sqs': [
            (r"'", Literal.String.Single, '#pop'),
            (r"\\'", Literal.String.Escape),
            (r"[^\n\\']*", Literal.String.Single),
        ],
    }
