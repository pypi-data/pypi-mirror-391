# -*- coding: utf-8 -*-
# rotom - a simple python library used to draw text-based 2d grid game map and informations
# Copyright (c) 2024 PrinceBiscuit <redsawbiscuit@gmail.com>
# License: MIT

__version__ = "0.1.0"

import re

class Char:

    EOL = '\n'

class Ascii:

    RESET = '\033[0m'
    '''reset all styles'''

    BOLD = '\033[1m'
    '''bold text'''

    UNDERLINE = '\033[4m'
    '''underlined text'''

    RED = '\033[31m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

class AsciiColor:
    '''record color'''

    @staticmethod
    def parse_color(col, is_background = False):
        '''parse color from different formats'''

        if col is None:
            return None

        if isinstance(col, tuple) and len(col) == 3:
            return AsciiColor(*col, is_background)
        
        if isinstance(col, str):
            # parse hex color
            if col.startswith('#') and len(col) == 7:
                r = int(col[1:3], 16)
                g = int(col[3:5], 16)
                b = int(col[5:7], 16)
                return AsciiColor(r, g, b, is_background)
            
        if isinstance(col, AsciiColor):
            return col
        
        return None

    def __init__(self, r, g, b, is_background = False):
        self.r = r
        self.g = g
        self.b = b
        self.is_background = is_background

    @property
    def ascii(self):
        '''format to terminal color code'''
        if self.is_background:
            return f'\033[48;2;{self.r};{self.g};{self.b}m'
        return f'\033[38;2;{self.r};{self.g};{self.b}m'

def clear_console():
    print("\033c", end="")  # 或者 print("\033[2J\033[H", end="")

def lenx(s):
    '''get the length of a string that showing in terminal instead of raw length
    for example '\033[31mHello\033[0m' should be 5 instead of 13'''

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    clean_text = ansi_escape.sub('', s)
    return len(clean_text)

def fg_color(r,g,b):
    '''font color'''
    return f'\033[38;2;{r};{g};{b}m'

def bg_col(r,g,b):
    '''background color'''
    return f'\033[48;2;{r};{g};{b}m'

def align(str1, length, align_type = 'center', pad_char = ' '):
    '''align a string to a certain length'''

    current_length = lenx(str1)
    if current_length >= length:
        return str1

    padding_length = length - current_length

    if align_type == 'left':
        padding = pad_char * padding_length
        return str1 + padding
    elif align_type == 'right':
        padding = pad_char * padding_length
        return padding + str1
    elif align_type == 'center':
        left_padding_length = padding_length // 2
        right_padding_length = padding_length - left_padding_length
        left_padding = pad_char * left_padding_length
        right_padding = pad_char * right_padding_length
        return left_padding + str1 + right_padding
    
    return str1

def get_longest_line_len(s):
    '''find the length of the longest line in a string'''

    if '\n' not in s:
        return lenx(s)
    lines = s.splitlines()
    return max(lenx(line) for line in lines)

def vertical_combine(str1, str2, sep = ' '):
    '''combine two ascii arts vertically'''

    if sep is None:
        return f"{str1}\n{str2}"
    
    if not isinstance(sep, str):
        sep = str(sep)
        if len(sep) == 0:
            return f"{str1}\n{str2}"
        sep = sep[0]

    if len(sep) == 0:
        return f"{str1}\n{str2}"
    
    if len(sep) > 1:
        sep = sep[0]

    longest_length1 = get_longest_line_len(str1)
    longest_length2 = get_longest_line_len(str2)
    sep_line = sep * max(longest_length1, longest_length2)
    return f"{str1}\n{sep_line}\n{str2}"

def pad_to_length(s, length, pad_char = ' '):
    '''pad a string to a certain length'''

    current_length = lenx(s)
    if current_length >= length:
        return s
    padding = pad_char * (length - current_length)
    return s + padding

def horizontal_combine(str1, str2, sep = ' '):
    '''combine two ascii arts horizontally, this should be complex than vertical combine'''

    lines1 = str1.splitlines()
    length_1 = len(lines1)

    lines2 = str2.splitlines()
    length_2 = len(lines2)

    longest_line1 = max(lenx(l) for l in lines1) if lines1 else 0
    default_pad1 = ' ' * longest_line1

    result = []
    total_count = max(length_1, length_2)
    for i in range(total_count):
        line1 = pad_to_length(lines1[i], longest_line1) if i < length_1 else default_pad1
        line2 = lines2[i] if i < length_2 else ''
        result.append(f"{line1}{sep}{line2}")
    return '\n'.join(result)

def add_style(s, col, bg_col, bold, underline):
    '''handle border style'''

    col = AsciiColor.parse_color(col)
    bg_col = AsciiColor.parse_color(bg_col, is_background=True)
    if col is None and bg_col is None and not bold and not underline:
        return s

    style_prefix = ''
    if col is not None:
        style_prefix += col.ascii

    if bg_col is not None:
        style_prefix += bg_col.ascii

    if bold:
        style_prefix += Ascii.BOLD

    if underline:
        style_prefix += Ascii.UNDERLINE

    if Char.EOL not in s:
        return f"{style_prefix}{s}{Ascii.RESET}"

    styled_lines = []
    for line in s.splitlines():
        styled_lines.append(f"{style_prefix}{line}{Ascii.RESET}")
    return '\n'.join(styled_lines)

    
def add_border(
        content,
        min_length = 0,
        min_height = 0, 
        corner_char = '+', 
        horizontal_char = '-', 
        vertical_char = '|',
        border_color = None,
        border_background_color = None,
        border_bold = False,
        border_underline = False
    ):
    '''render content on a board'''

    lines = content.splitlines()
    longest_line = max(lenx(line) for line in lines) if lines else 0
    longest_line = max(longest_line, min_length)

    top_border = corner_char + (horizontal_char * (longest_line + 2)) + corner_char
    top_border = add_style(top_border, border_color, border_background_color, border_bold, border_underline)
    bottom_border = top_border

    if len(lines) < min_height:
        for _ in range(min_height - len(lines)):
            lines.append('')

    _vc = add_style(vertical_char, border_color, border_background_color, border_bold, border_underline)

    board_lines = [top_border]
    for line in lines:
        padding = ' ' * (longest_line - lenx(line))
        board_lines.append(f"{_vc} {line}{padding} {_vc}")
    board_lines.append(bottom_border)

    return '\n'.join(board_lines)

class Tile:
    '''represent a tile in the game map'''

    def __init__(
        self, 
        char='·', 
        color=None,
        background_color=None,
        bold=False,
        underline=False
    ):
        '''
        Initialize a tile.
        :param char: character to display
        :param color: color of the character, can be (r,g,b) tuple or hex string like '#RRGGBB'
        :param background_color: background color of the character, can be (r,g,b) tuple or hex string like '#RRGGBB'
        :param bold: whether the character is bold
        :param underline: whether the character is underlined'''

        self.char = char
        self.bold = bold
        self.color = AsciiColor.parse_color(color)
        self.background_color = AsciiColor.parse_color(background_color, is_background=True)
        self.underline = underline
    
    def __str__(self):
        return add_style(self.char, self.color, self.background_color, self.bold, self.underline)

class Tilemap:
    '''a simple terminal board to render tiles
    to represent the game map or other things'''

    def __init__(
        self, 
        width=10, 
        height=10, 
        default_tile_char = '·',
        default_tile_color = None,
        default_tile_background_color = None,
        default_tile_bold = False,
        default_tile_underline = False
    ):
        self.__width = width
        self.__height = height
        self.__default_tile = Tile(
            char=default_tile_char,
            color=default_tile_color,
            background_color=default_tile_background_color,
            bold=default_tile_bold,
            underline=default_tile_underline
        )
        self.__tiles = [[self.__default_tile for _ in range(width)] for _ in range(height)]

    def _is_valid_pos(self, x, y):
        '''check if (x, y) is a valid position'''

        return 0 <= x < self.__width and 0 <= y < self.__height

    def set_tile(self, x, y, tile):
        '''Set a tile at position (x, y)'''

        if not self._is_valid_pos(x, y):
            return False

        if tile is None:
            tile = Tile()

        elif isinstance(tile, str):
            if len(tile) == 0:
                tile = Tile()

            elif len(tile) == 1:
                tile = Tile(char=tile)

            else:
                tile = Tile(char=tile[0])

        elif isinstance(tile, Tile):
            pass

        else:
            '''invalid tile type'''

            return False

        self.__tiles[y][x] = tile
        return True

    def set_char(self, x, y, char, color=None, bold=False, underline=False):
        '''Set a character at position (x, y)'''

        tile = Tile(char=char, color=color, bold=bold, underline=underline)
        self.set_tile(x, y, tile)

    def clear(self):
        '''set all tiles to default'''

        self.__tiles = [[self.__default_tile for _ in range(self.__width)] for _ in range(self.__height)]

    def render(self) -> str:
        '''Render the map to a string'''

        output = []
        for row in self.__tiles:
            output.append(' '.join(str(tile) for tile in row))
        return '\n'.join(output)
    
    def __str__(self):
        return self.render()
    
    def __call__(self, *args, **kwds):
        return self.render()
    
class _Info:
    '''represent a single information line'''

    def __init__(
        self, 
        title:str, 
        content:str, 
        title_bold = False, 
        content_bold = False,
        title_color = None, 
        content_color = None,
        title_underline = False,
        content_underline = False,
        title_bg_color = None,
        content_bg_color = None
    ):
        '''Initialize an information line.'''
        self.title = title
        self.content = content
        self.title_color = title_color
        self.content_color = content_color
        self.title_bold = title_bold
        self.content_bold = content_bold
        self.title_underline = title_underline
        self.content_underline = content_underline
        self.title_bg_color = title_bg_color
        self.content_bg_color = content_bg_color

    def set_content(self, content:str):
        self.content = content

    def __len__(self):
        return lenx(str(self))

    def __str__(self):
        _title = add_style(self.title, self.title_color, self.title_bg_color, self.title_bold, self.title_underline)
        _content = add_style(self.content, self.content_color, self.content_bg_color, self.content_bold, self.content_underline)
        return f"{_title}: {_content}"

class _InfoGroup:
    '''show informations on the right side of the map'''

    def __init__(self, title = None, title_align = "center"):
        self.title = title
        self.title_align = title_align
        self.infos = { }

    def add_info(self, title:str, info:_Info = None) -> bool:
        '''Add an information line.'''

        if len(title) == 0 or title in self.infos:
            return False

        info = info if info is not None else _Info(title, "")
        self.infos[title] = info

    def set_info(self, title:str, content:str) -> bool:
        '''Set the content of an information line.'''

        if title not in self.infos:
            _info = _Info(title, content)
            return self.add_info(title, _info)

        self.infos[title].set_content(content)
        return True
    
    def render(self) -> str:
        '''Render the information board to a string.'''

        lines = []
        for key in self.infos:
            lines.append(str(self.infos[key]))

        if self.title != None and len(self.title) > 0:
            _longest_line = max(lenx(line) for line in lines) if lines else 0
            _title = align(self.title, _longest_line, self.title_align)
            lines.insert(0, _title)

        total = '\n'.join(lines)
        boarded = add_border(total, min_length=30)
        return boarded

    def __str__(self):
        return self.render()
    
    def __call__(self, *args, **kwds):
        return self.render()
    
class InfoBoard:
    '''a board to show information'''
    
    DEFAULT_GROUP = "__default__"

    def __init__(self):
        self.__groups = { }
        self.__groups.setdefault(InfoBoard.DEFAULT_GROUP, _InfoGroup())

    def _get_group(self, group:str) -> _InfoGroup:
        '''Get an information group by name.'''

        if group is None or group == '':
            return self.__groups[InfoBoard.DEFAULT_GROUP]

        if group not in self.__groups:
            self.__groups[group] = _InfoGroup()
        return self.__groups[group]

    def add_info(self, title:str, info:_Info = None, group:str=None) -> bool:
        '''Add an information line to a group.'''

        group = self._get_group(group)
        return group.add_info(title, info)
    
    def set_info(self, title:str, content:str, group:str=None) -> bool:
        '''Set the content of an information line in a group.'''

        group = self._get_group(group)
        return group.set_info(title, content)
    
    def render(self) -> str:
        '''Render the information board to a string.'''

        group_strs = []
        for key in self.__groups:
            group_strs.append(str(self.__groups[key]))
        
        if len(group_strs) == 0:
            return ''
        
        if len(group_strs) == 1:
            return group_strs[0]
        
        if len(group_strs) == 2:
            return vertical_combine(group_strs[0], group_strs[1], sep='')
        
        result = group_strs[0]
        for group_str in group_strs[1:]:
            result = vertical_combine(result, group_str, sep='')
        return result
    
    def __str__(self):
        return self.render()
    
    def __call__(self, *args, **kwds):
        return self.render()
            

if __name__ == "__main__":

    # import rotom
    # tilemap = Tilemap(5, 5)
    tilemap = Tilemap(8, 8)
    tilemap.set_char(5, 5, '@')

    infos = InfoBoard()
    infos.set_info("title", "content")

    result = vertical_combine(tilemap(), infos(), sep='/')
    print(result)

    # W, H = 12, 12
    # Map = Tilemap(W, H, default_tile_char='·', default_tile_color=(100,100,100))
    # agent_tile = Tile(char='@', color="#942c4b", bold=False)

    # board = InfoBoard()
    # board.set_info("Position", "(0, 0)")
    
    # import time
    # x = 0
    # y = 0
    # while 1:
    #     Map.clear()
    #     Map.set_tile(x, y, agent_tile)
    #     clear_console()
    #     _map = add_border(Map.render())
    #     _board = board.render()
    #     print(horizontal_combine(_map, _board, sep='   '))

    #     x += 1
    #     board.set_info("Position", f"({x}, {y})")
    #     if x >= W:
    #         break

    #     time.sleep(1)