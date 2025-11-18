from textwrap import wrap

from .coords import Size, Position, Vector
from .grid_drawing import GridDrawing
from .cell import ConnectorCell
# from .helpers import find_colour_from_key

def schematic_svg(board, gridlines=False):
    # Draw PCN SVG, returning it in ElementTree XML
    
    # Start with grid with border of one added (for the pins)
    # - Put any pins on left or right on their sides
    # - If gaps on left, go through half the row (L->R) looking for pin
    # - If gaps in the right, go though all the row (R->L) looking for pin
    # - If gaps on left, go through all the row (L->R) looking for pin
    # - Go through board (scanning down first), putting pins
    #   on the top (not corners). If coallescing GND pins, skip them
    # - If not wide enough, see how many left over, widen by that much
    # - If coallescing, Remove GND pins, and put on bottom middle
    # - Try to space out top pins
    
    left = [None] * board.source.size.height
    right = [None] * board.source.size.height
    top = [None] * board.source.size.width
    
    # Coordinates are like this:
    #         3 |   4 |
    #           |     |
    #      +----x-----x--
    #      |  (4,2) (6,2) [space out if not fully populated, extend else]
    #   1  | 
    # -----X (2,4)       (W,4) X-----
    #      |                   |
    #   2  |                   |
    # -----x (2,6)       (W,6) X----
    #     
    
    right_side = board.source.size.width+2
    
    for top_to_left, top_to_right in zip(board.layout[0], reversed(board.layout[0])):
        for cell_to_left in top_to_left.iter_down():
            if isinstance(cell_to_left, ConnectorCell):
                # print(cell_to_left)
                y = cell_to_left.element.position.y
                if not cell_to_left.schemed and not left[y]:
                    left[y] = cell_to_left
                    cell_to_left.schemed = Position(2, y*2+4)
        for cell_to_right in top_to_right.iter_down():
            if isinstance(cell_to_right, ConnectorCell):
                y = cell_to_right.element.position.y
                if not cell_to_right.schemed and not right[y]:
                    right[y] = cell_to_right
                    cell_to_right.schemed = Position(right_side, y*2+4)
         
    remaining = [cell for cell in board.connectors.values() if not cell.schemed]
    if len(remaining) > board.layout.size.width:
        raise NotImplementedError(f'Need code if too many pins, these are left {remaining}')
    else:
        for nx, cell_to_top in enumerate(remaining):
            x = 2 + (board.layout.size.width) * (nx+1) / (len(remaining)+1)
            top[nx] = cell_to_top
            cell_to_top.schemed = Position(x, 2)
            
    # print([(f'{cell.schemed.x}x{cell.schemed.y}' if cell else 'None') for cell in left])
    # print([(f'{cell.schemed.x}x{cell.schemed.y}' if cell else 'None') for cell in right])
    # print([(f'{cell.schemed.x}x{cell.schemed.y}' if cell else 'None') for cell in top])
    # print(right)
    # print(top)
      
    ############# Draw it all ################
    
    grid = GridDrawing(
        size=board.size + Size(4, 6),
        border=Size(0, 0),
        grid_size=board.config['metadata']['grid_size'],
        grid_unit=board.config['metadata']['grid_unit'],
        scale=board.config['metadata']['scale'],
        parts_dict=None)

    schematic = grid.g(id='schematic')

    c2 = grid.coords_to
    appearance = board.config['appearance']['schematic']
   
    line_col = board.colour(appearance['tick-colour'])
    line_len = appearance['tick']
    line_wid = appearance['tick-width']
    
    schematic.add(grid.rect(id="outline",
                       fill='none',
                       stroke=board.colour(appearance['outline-colour']),
                       stroke_width=c2.clen(appearance['outline-width']),
                       insert=c2.cabs(Position(2, 2)),
                       size=c2.cabs(board.size + Size(0, 2))))

    wrap_at = int((board.source.size.width - 2) / 1.1*appearance['label-font-size'])
    # print(wrap_at)
    lines = wrap(board.config['metadata']['label'], width=wrap_at)
    
    group = grid.g(id=f'label')
    for y, line in enumerate(lines):
        
        insert = Position(board.source.size.width/2+2,
                          board.source.size.height/3+3 +
                          y * 1.5*appearance['name-font-size'] )
        group.add(grid.text(insert=c2.cabs(insert),
                           text_anchor='middle',
                           fill=board.colour(appearance['name-colour']),
                           font_size=c2.clen(appearance['name-font-size']),
                           font_family=appearance['name-font'],
                           text=line))
    schematic.add(group)


    for cell in [cell for cell in left if cell]:
        tick_vector = Vector(-appearance['tick'], 0)
        id_offset = Vector(-appearance['id-font-size']*0.75,
                           -appearance['id-font-size']*0.5)
        label_offset = Vector(appearance['label-font-size']*0.4,
                              appearance['label-font-size']*0.3)
       
        connector = connector_draw(board, grid, cell, appearance, c2, tick_vector,
                                   id_offset, 'end', label_offset, 'start')
        schematic.add(connector)
        
    for cell in [cell for cell in right if cell]:
        tick_vector = Vector(appearance['tick'], 0)
        id_offset = Vector(appearance['id-font-size']*0.75,
                           -appearance['id-font-size']*0.5)
        label_offset = Vector(-appearance['label-font-size']*0.4,
                              appearance['label-font-size']*0.3)
       
        connector = connector_draw(board, grid, cell, appearance, c2, tick_vector,
                                   id_offset, 'start', label_offset, 'end')
        schematic.add(connector)

    for cell in [cell for cell in top if cell]:
        tick_vector = Vector(0, -appearance['tick'])
        id_offset = Vector(-appearance['id-font-size']*0.5,
                           -appearance['id-font-size']*0.75)
        label_offset = Vector(0,
                              appearance['label-font-size']*1.1)
       
        connector = connector_draw(board, grid, cell, appearance, c2, tick_vector,
                                   id_offset, 'end', label_offset, 'middle')
        schematic.add(connector)

    grid.add(schematic)

    if gridlines:
        grid.add(grid.grid_lines(*board.size))

    return grid.get_xml()

def connector_draw(board, grid, cell, appearance, c2, tick_vector, id_offset, 
                   id_text_anchor, label_offset, label_text_anchor):
    
    group = grid.g(id=f'connector{cell.cid}pin')
        
    group.add(grid.line(stroke=board.colour(appearance['tick-colour']),
                    stroke_width=c2.clen(appearance['tick-width']),
                    start=c2.cabs(cell.schemed),
                    end=c2.cabs(cell.schemed + tick_vector)))
    
    group.add(grid.text(insert=c2.cabs(cell.schemed + id_offset),
                    text_anchor=id_text_anchor,
                    fill=board.colour(appearance['id-colour']),
                    font_size=c2.clen(appearance['id-font-size']),
                    font_family=appearance['id-font'],
                    text=str(cell.number)))

    group.add(grid.text(insert=c2.cabs(cell.schemed + label_offset),
                    text_anchor=label_text_anchor,
                    fill=board.colour(appearance['label-colour']),
                    font_size=c2.clen(appearance['label-font-size']),
                    font_family=appearance['label-font'],
                    text=cell.label))

    terminal = Size(appearance['terminal-size'], appearance['terminal-size'])
    group.add(grid.rect(id=f'connector{cell.cid}terminal',
                        fill='none',
                        insert=c2.cabs(cell.schemed + tick_vector - terminal/2),
                        size=c2.crel(terminal)))

    return group
