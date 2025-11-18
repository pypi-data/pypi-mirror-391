import svgwrite

from .coords import Size, CoordsTo, Position, Vector
from .pcb_shape_mixin import PCBShapeMixin
from .helpers import find_part_code_from_key, find_colour_from_key
from .cell import ConnectorCell, PartCell

import logging
log = logging.getLogger(__name__)

class GridDrawing(svgwrite.Drawing, PCBShapeMixin):
    # Construct an SVG drawing based on a grid
    # All input uses a cell size of 1.0x1.0
    # All output elements use a cell size of scale (e.g 7.2 x 7.2)
    # The grid can have a border, in which case cells can be drawn outsize the grid
    # The SVG w/h will be written in svgwrite unit (if specified)
    units = {
        'mm': svgwrite.mm, 
        'cm': svgwrite.cm, 
        'inch': svgwrite.inch,
        'px': svgwrite.px,
        'none': 1}

    def __init__(self, size, grid_size, grid_unit, scale, parts_dict, border=Size(0, 0)):
        
        # self.filename = filename
        self.size = size
        self.grid_size = grid_size
        self.grid_unit = grid_unit
        self.scale = scale
        self.parts_dict = parts_dict
        self.border = border
        self.coords_to = CoordsTo(border, Position(0, 0), scale)
        
        try:
            SVG_size = ((size + border * 2) * grid_size) * self.units[grid_unit]
        except KeyError:
            raise ValueError('Unrecognized unit: {grid_units}')
        
        viewbox_size = (size + border * 2) * self.scale
        viewbox_string = f'0 0 {int(viewbox_size.width)} {int(viewbox_size.height)}'
        
        super().__init__(
            profile='tiny',
            debug=True,
            size=SVG_size,
            viewBox=viewbox_string
        )
        
    def __repr__(self):
        return f'GridDrawing(size={self.size}, grid_size={self.grid_size}, grid_units={self.grid_units}, scale={self.scale}, border={self.border})'
    
    def grid_lines(self, width, height):
        c2 = CoordsTo(self.border, 0, self.scale)
        group = self.g(id='grid-lines')
        
        for x in range(self.size.width + 1):
            stroke_dasharray="none"
            if x % 2 == 1:
                stroke_dasharray="18,6"
            group.add(self.line(
                c2.cabs(Position(x, 0)), 
                c2.cabs(Position(x, self.size.height)),
                stroke_dasharray=stroke_dasharray,
                stroke='magenta', stroke_width=1))
        for y in range(self.size.height + 1):
            stroke_dasharray="none"
            if y % 2 == 1:
                stroke_dasharray="8,16"
            group.add(self.line(
                c2.cabs(Position(0, y)),
                c2.cabs(Position(self.size.width, y)),
                stroke_dasharray=stroke_dasharray,
                stroke='magenta', stroke_width=1))
        
        return group
    
    def draw_text(self, cell, text_dict, colour_dict):
        c2 = CoordsTo(self.border, cell.position, self.scale, cell.size)
        text = text_dict[cell.text_key]
        # print(f'text', text)
        # print(f'text["text"]: "{text["text"]}"')
        x, y = c2.pabs(Position(0.5, 0.5)) # Rotate about center of part
        fill = find_colour_from_key(colour_dict, text['colour'], None)
        text_svg = self.text(
                text['text'],
                # insert=c2.prel(Position(0.5, 0.5)),
                insert=c2.prel(Size(-0.5, text['size'] * 0.18)),
                fill=fill,
                font_family=text['font'],
                font_size=c2.clen(text['size']),
                text_anchor='start',
                transform=f'translate({x},{y}) rotate({text["angle"]})')
                # transform=f'rotate({text["angle"]})')
        text_svg.update({'xml:space': 'preserve'})
        return text_svg
    
    def draw_holepath(self, *args, **kwargs):
        pass
    
    def draw_ellipse(self, group, id_dict, fill, stroke, stroke_width, expargs):
        # print('Ellipse', fill, stroke, stroke_width, expargs)
        if len(expargs) != 4:
            raise ValueError(f'Ellipses must have 4 args: {expargs}')
        group.add(self.ellipse(
            **id_dict,
            center=(expargs[0], expargs[1]),
            r=(abs(expargs[2]), abs(expargs[3])),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width))

    def draw_circle(self, group, id_dict, fill, stroke, stroke_width, expargs):
        # print('Circle', fill, stroke, stroke_width, expargs)
        if len(expargs) != 3:
            raise ValueError(f'Circles must have 3 args: {expargs}')
        group.add(self.circle(
            **id_dict,
            center=(expargs[0], expargs[1]),
            r=(abs(expargs[2])),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width))

    def draw_rect(self, group, id_dict, fill, stroke, stroke_width, expargs):
        # print('Rect', fill, stroke, stroke_width, expargs)
        if len(expargs) != 4:
            raise ValueError(f'Rectangles must have 4 args: {expargs}')
        # if str(fill) == '#cc1414':
        #     print(fill, stroke, stroke_width, expargs)
        
        minx = min(expargs[0], expargs[0]+expargs[2])
        miny = min(expargs[1], expargs[1]+expargs[3])
        group.add(self.rect(
            **id_dict,
            insert=(minx, miny),
            size=(abs(expargs[2]), abs(expargs[3])),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width))

    def draw_rectround(self, group, id_dict, fill, stroke, stroke_width, expargs):
        # print('Rect', fill, stroke, stroke_width, expargs)
        if len(expargs) != 6:
            raise ValueError(f'Rounded rectangles must have 6 args: {expargs}')
        minx = min(expargs[0], expargs[0]+expargs[2])
        miny = min(expargs[1], expargs[1]+expargs[3])
        group.add(self.rect(
            **id_dict,
            insert=(minx, miny),
            size=(abs(expargs[2]), abs(expargs[3])),
            rx=abs(expargs[4]), ry=abs(expargs[5]),
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width))

    def draw_path(self, group, id_dict, fill, stroke, stroke_width, expargs):
        # print('Path', fill, stroke, stroke_width, expargs)
        group.add(self.path(
            **id_dict,
            d=expargs,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width))

    drawers = {
        'holepath': draw_holepath,
        'ellipse': draw_ellipse,
        'circle': draw_circle,
        'rect': draw_rect,
        'rectround': draw_rectround,
        'path': draw_path,
    }
    
    ops_dict = {
        'draw-in': [],
        'flip-to': ['flip'],
        'flop-to': ['flop'],
        'flipflop-to': ['flip', 'flop'],
        'transpose-to': ['transpose'],
        'transpose-flip-to': ['transpose', 'flip'],
        'transpose-flop-to': ['transpose', 'flop'],
        'transpose-flipflop-to': ['transpose', 'flip', 'flop']
    }
    
    def shadow_draw(self, drawer, c2, shadow, group, id_dict, fill,
                    stroke, stroke_width, args):
        # log.info(f'Drawing shape with shadow {shadow}, fill {fill}, type {type(fill)}')
        if str(fill) == 'none' and str(stroke) == 'none':
            return
        
        if shadow:
            if stroke != 'none':
                log.info(f'Shadowing shapes with stroke "{stroke}" does not work well')
            
            try:
                offset = Vector(shadow[0], shadow[1])
            except TypeError:
                offset = Vector(shadow, shadow)

            # print('before transpose_only', offset)
            offset = c2.transpose_only(offset)
            # print('after transpose_only', offset)

            if offset[0] == offset[1]:
                # For equal shadows, using the stroke to draw looks nicer at the
                # corners, and produces less SVG
                shadow_stroke_width = c2.clen(offset[0])
                
                expargs = c2.expand_args_list(args)
                drawer(self, group, id_dict, 'none', fill[0],
                       shadow_stroke_width*2, expargs)

                expargs = c2.offset(offset/2).expand_args_list(args)
                drawer(self, group, id_dict, 'none', fill[1],      
                       shadow_stroke_width, expargs)

                expargs = c2.offset(-offset/2).expand_args_list(args)
                drawer(self, group, id_dict, 'none', fill[2],
                       shadow_stroke_width, expargs)
            else:
                # For unequal shadows, we have to use fill to draw shadow, as
                # SVG strokes can't have different widths and heights (like
                # a wide calligraphy pen)
                if offset[0] == 0:
                    shadow_vectors = [Vector(0, 1)]
                    corner_vectors = []
                elif offset[1] == 0:
                    shadow_vectors = [Vector(1, 0)]
                    corner_vectors= []
                else:
                    shadow_vectors = [Vector(1,1), Vector(0,1), Vector(1,0)]
                    corner_vectors = [Vector(1,-1), Vector(-1,1)]
                    
                print('offset', offset)
                print('shadow_vectors', shadow_vectors)
                print('corner_vectors', corner_vectors)
                for v in corner_vectors:
                    expargs = c2.offset(offset*v).expand_args_list(args)
                    drawer(self, group, id_dict, fill[0], 'none',
                           0, expargs)
                
                for v in shadow_vectors:
                    expargs = c2.offset(offset*v).expand_args_list(args)
                    drawer(self, group, id_dict, fill[1], 'none',
                           0, expargs)
                
                for v in shadow_vectors:
                    expargs = c2.offset(-offset*v).expand_args_list(args)
                    drawer(self, group, id_dict, fill[2], 'none',
                           0, expargs)

        expargs = c2.expand_args_list(args)
        drawer(self, group, id_dict, fill, stroke, stroke_width, expargs)
        
    def draw_part(self, cell, font, colour_dict):
        # Draw part or connector
        
        # Both have the part_key set
        part_code, part_ops = find_part_code_from_key(self.parts_dict, cell.part_key)
        # colour = find_colour_from_key(colour_dict, cell.colour_key, None)
        
        part_ops.extend(cell.part_ops)
            
        if isinstance(cell, ConnectorCell):
            gid = f'pin{cell.number}'
            name = f'{cell.number:<2}'
            # print(part_ops)
        else:
            try:
                name = part_code['name']
            except KeyError:
                # Part does not have name
                name = cell.colour_key + cell.part_key
            except TypeError:
                # Part is None (not known)
                name = cell.colour_key + cell.part_key
            x, y = cell.element.position
            w, h = cell.size
            gid = f'{name}-cell:{x}.{y}-size:{w}x{h}'
            
        group = self.g(id=gid)
        
        if part_code:
  
            for shape in part_code['shapes']:
                c2 = CoordsTo(self.border, cell.position, self.scale, Size.one())
                fill, stroke, stroke_width =  self.style(shape, colour_dict,
                                                         cell.colour_key, c2)

                try:
                    drawer = self.drawers[shape['type']]
                except KeyError:
                    raise ValueError(f'Unknown shape type: {shape["type"]}')

                try:
                    id_dict = {'id': f'connector{cell.cid}{shape["id"]}'}
                except (AttributeError, KeyError):
                    id_dict = {}

                # print(shape)
                try:
                    shadow = shape['shadow']
                except KeyError:
                    shadow = 0

                if 'draw-in' in shape:
                    try:
                        step = int(shape['step'])
                    except KeyError:
                        step = 1
                        
                    part_cells = self.part_cells(cell, part_ops, step)
                    # print('Part cells by type')
                    # for k, v in part_cells.items():
                    #     l = '|'.join([str(c) for c in v])
                        # print(f'{k} {l}')
                        
                    for op_name, ops_list in self.ops_dict.items():
                        if op_name in shape:
                            for location in shape[op_name]:
                                for op_cell in part_cells[location]:
                                    c2 = CoordsTo(self.border, op_cell.position,
                                                  self.scale, cell.size, 
                                                  ops=ops_list+part_ops, step=step)
                                    self.shadow_draw(drawer, c2, shadow, group,
                                                id_dict, fill, stroke,
                                                stroke_width, shape['args'])

                else:
                    c2 = CoordsTo(self.border, cell.position, self.scale,
                                  cell.size, ops=part_ops)
                    # expargs =  c2.expand_args_list(shape['args'])
                    # if cell.string == 'c-':
                    #     print('XXXX', repr(cell))
                    #     print('XXXX', shape['args'])
                    #     print('XXXX', expargs)
                    #     print('XXXX', c2)
                    # drawer(self, group, id_dict, fill, stroke, stroke_width, expargs)
                    self.shadow_draw(drawer, c2, shadow, group,
                                     id_dict, fill, stroke,
                                     stroke_width, shape['args'])
            
        else:
            fill = find_colour_from_key(colour_dict, '?', cell.colour_key)
            c2 = CoordsTo(self.border, cell.position, self.scale, cell.size)
            position = c2.cabs(Position(0.1, 0.1))
            size = c2.jump(Size(0.8, 0.8))
            stroke_width = c2.clen(0.05)
            font_size = 1
            group.add(self.rect(
                position,
                size,
                fill=fill,
                stroke='magenta',
                stroke_width=stroke_width))
            group.add(self.text(
                name,
                c2.pabs(Position(0.5, 0.5)) + c2.crel(Size(0, font_size * 0.36)),
                fill='magenta',
                font_family = font,
                font_size=c2.clen(font_size),
                text_anchor='middle'
                ))
        return group
    
    @staticmethod
    def part_array(cell):
        # Make up an sub-array of the cell's Array2D that make up this part
        # FIXME Will probably barf for an offset part on bottom row
        array = []
        row_start = cell
        for _ in range(cell.size.height):
            row = []
            part_cell = row_start
            for _ in range(cell.size.width):
                row.append(part_cell)
                part_cell = part_cell.right
            array.append(row)
            row_start = row_start.down
        return array

    @classmethod
    def part_cells(cls, cell, part_ops, step=1):
        if not isinstance(cell, PartCell):
            raise AssertionError(f'Cell is not a part: {cell}')

        result = {}
        array = cls.part_array(cell)
        
        if 'transpose' in part_ops:
            array = [list(x) for x in zip(*array)]
            
        result['top-left'] = [array[0][0]]
        result['top-middle'] = array[0][step:-step:step]
        result['top-right'] = [array[0][-step]]
        
        result['middle-left'] = []
        result['middle'] = []
        result['middle-right'] = []

        for row in array[step:-step:step]:
            result['middle-left'].append(row[0])            
            result['middle'].extend(row[step:-step:step])
            result['middle-right'].append(row[-step])
            
        result['bottom-left'] = [array[-step][0]]
        result['bottom-middle'] = array[-step][step:-step:step]
        result['bottom-right'] = [array[-step][-step]]
        
        return result
    
    @staticmethod
    def style(shape, colour_dict, cell_colour_key, c2):
            
        try:
            fill_colour_key = shape['fill']
        except KeyError:
            fill = 'none'
        else:
            fill = find_colour_from_key(colour_dict, fill_colour_key,
                                            cell_colour_key)
        try:
            stroke_colour = shape['stroke']
        except KeyError:
            stroke = 'none'
        else:
            stroke = find_colour_from_key(colour_dict, stroke_colour,
                                              cell_colour_key)

        try:
            stroke_width = shape['stroke-width']
        except KeyError:
            stroke_width = 0
        else:
            stroke_width = c2.clen(stroke_width)
        
        return fill, stroke, stroke_width
        
