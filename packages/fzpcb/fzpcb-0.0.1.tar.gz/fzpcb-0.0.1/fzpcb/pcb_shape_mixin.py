import math
from .coords import Dir, Vector, Size, CoordsTo, Position
from .helpers import find_part_code_from_key, find_colour_from_key

class PCBShapeMixin:
    # Mixin extending GridDrawing with the ability
    # to generate SVG to draw the PCB for the breadboard image
    #
    # Boards has the layout array, colours, and parts
    # We know border and scale
    
    def pcb_outline(self, board):
        stroke_width = board.config['appearance']['pcb']['outline']
        stroke_colour_key  =  board.config['appearance']['pcb']['outline-colour']
        stroke = board.colour(stroke_colour_key)
        
        outline_path = OutlinePath(board, self.parts_dict, holes=False)

        path_d = outline_path.to_d(self.border, Size.zero(), self.scale)
        outline = self.path(id='PCB-outline',
                            stroke=stroke, fill='none',
                            stroke_width=stroke_width * self.scale,
                            stroke_linejoin='round', d=path_d)

        return outline
    
    def pcb_shape(self, board):
        
        stroke_width = board.config['appearance']['breadboard']['highlight']
        offset = Size(stroke_width, stroke_width) / 2
        
        # board.print_array()
        outline_path = OutlinePath(board, self.parts_dict)
        # print(outline_path.dirs)

        # print(outline_path)
        pcb_colour = board.config['appearance']['breadboard']['PCB-colour']
        highlight = board.colour((pcb_colour, 2))
        lowlight = board.colour((pcb_colour, 1))
        fill = board.colour((pcb_colour, 0))
        
        group = self.g(id='PCB-board')
        
        path_d = outline_path.to_d(self.border, Size.zero(), self.scale)
        group.add(self.path(stroke=fill, fill='none',
                            stroke_width=stroke_width * 2 * self.scale,
                            stroke_linejoin='round', d=path_d))

        path_d = outline_path.to_d(self.border, -offset, self.scale)
        group.add(self.path(stroke=highlight, fill='none',
                            stroke_width=stroke_width * self.scale,
                            stroke_linejoin='round', d=path_d))

        path_d = outline_path.to_d(self.border, offset, self.scale)
        group.add(self.path(stroke=lowlight, fill='none',
                            stroke_width=stroke_width * self.scale,
                            stroke_linejoin='round', d=path_d))

        path_d = outline_path.to_d(self.border, Size.zero(), self.scale)
        group.add(self.path(stroke='none', fill=fill, d=path_d))
               
        return group
        
class OutlinePath:
    def __init__(self, board, parts_dict, holes=True):
        self.board = board
        self.dirs = []
        self.holes = []
        # self.layout = board.config['layout']
        # self.notpcb = board.config['specials']['not-pcb']
        
        # Find a top left corner
        # board.source is a 2D layout of elements, with
        # element.char == config['specials']['empty'] for non-pcb parts
        # print(board.layout.source)
        for element in board.source.flatten():
            # print(f"Is {element} != '{board.config['specials']['empty']}'")
            if element.char != board.config['specials']['empty']:
                self.start = element
                self.dir_right(element)
                break
            
        # FIXME look for actual holes (cells with ' '), not just hole parts

        if holes:
            # Find the hole part paths
            for cell in board.parts:
                part_key, part_ops = find_part_code_from_key(parts_dict,
                                                                cell.part_key)
                if part_key != None:
                    for shape in part_key['shapes']:
                        if shape['type'] == 'holepath':
                            self.holes.append((cell, part_ops, shape['args']))
                            
            for cell in board.connectors.values():
                part_key, part_ops = find_part_code_from_key(parts_dict,
                                                                cell.part_key)
                if part_key != None:
                    for shape in part_key['shapes']:
                        if shape['type'] == 'holepath':
                            self.holes.append((cell, part_ops, shape['args']))
            
        # for hole in self.holes:
        #     print(f'Hole: {hole}')
        
    def __str__(self):
        return f'start = {self.start}\ndirs = {self.dirs}'

    def to_d(self, border, offset, scale):
        c2 = CoordsTo(border, offset, scale)
        d = ['M', *c2.cabs(self.start.position * Vector(1,2))]

        # FIXME only need to do this once per outline, not once per to_d()
        merged = self.merge_dirs(self.dirs)
        
        for this, count in merged[:-1]:
            if this == Dir.RIGHT:
                d.extend(['l', *c2.crel(Vector.one().right() * count)])
            elif this == Dir.DOWN:
                d.extend(['l', *c2.crel(Vector.two().down() * count)])
            elif this == Dir.LEFT:
                d.extend(['l', *c2.crel(Vector.one().left() * count)])
            elif this == Dir.UP:
                d.extend(['l', *c2.crel(Vector.two().up() * count)])
            else:
                raise AssertionError("Can't happen")
        d.append('z')

        for cell, part_ops, args in self.holes:
            c2 = CoordsTo(border, cell.position+offset, scale, part_size=cell.size, ops=part_ops)
            d.extend(c2.expand_args_list(args))
            
        return d
    
    @staticmethod
    def merge_dirs(dirs):
        # Turn [RIGHT, RIGHT, DOWN, RIGHT, DOWN, DOWN, DOWN] into
        #      [(RIGHT, 2), (DOWN, 1), (RIGHT, 1), (DOWN, 3)]
        merged = [(dirs[0], 1)]
        for dir in dirs[1:]:
            if merged[-1][0] == dir:
                merged[-1] = (dir, merged[-1][1]+1)
            else:
                merged.append((dir, 1))
        return merged
    
    def dir_right(self, element):
        # Arrived a top left corner
        # This could be the start
        if element.up:
            self.dir_up(element.up)
        elif element.right:
            self.dirs.extend([Dir.RIGHT])
            self.dir_right(element.right)
        elif element.down:
            self.dirs.extend([Dir.RIGHT, Dir.DOWN])
            self.dir_down(element.down)
        elif element.left:
            self.dirs.extend([Dir.RIGHT, Dir.DOWN, Dir.LEFT])
            self.dir_left(element.left)
        else:
            self.dirs.extend([Dir.RIGHT, Dir.DOWN, Dir.LEFT, Dir.UP])
            
    def dir_down(self, element):
        # Arrived a top right corner
        # Can't go down to the start
        if element.right:
            self.dir_right(element.right)
        elif element.down:
            self.dirs.extend([Dir.DOWN])
            self.dir_down(element.down)
        elif element.left:
            self.dirs.extend([Dir.DOWN, Dir.LEFT])
            self.dir_left(element.left)
        elif element.up:
            self.dirs.extend([Dir.DOWN, Dir.LEFT, Dir.UP])
            self.dir_up(element.up)
        else:
            raise AssertionError("Can't happen")

    def dir_left(self, element):
        # Arrived a bottom right corner
        # Can arrive at the start going left, if PCB is one unit high
        if element.down:
            self.dir_down(element.down)
        elif element.left:
            self.dirs.extend([Dir.LEFT])
            self.dir_left(element.left)
        elif element.up:
            self.dirs.extend([Dir.LEFT, Dir.UP])
            self.dir_up(element.up)
        elif element.right:
            self.dirs.extend([Dir.LEFT, Dir.UP])
            if element == self.start:
                return
            self.dirs.extend([Dir.RIGHT])
            self.dir_right(element.right)
        else:
            raise AssertionError("Can't happen")

    def dir_up(self, element):
        # Arrived a bottom left corner
        if element.left:
            self.dir_left(element.left)
        elif element.up:
            self.dirs.extend([Dir.UP])
            self.dir_up(element.up)
        elif element.right:
            self.dirs.extend([Dir.UP]) # Finish left edge
            if element == self.start:
                return
            self.dirs.extend([Dir.RIGHT])
            self.dir_right(element.right)
        elif element.down:
            self.dirs.extend([Dir.UP])
            if element == self.start:
                return
            self.dirs.extend([Dir.RIGHT, Dir.DOWN])
            self.dir_down(element.down)
        else:
            raise AssertionError("Can't happen")
