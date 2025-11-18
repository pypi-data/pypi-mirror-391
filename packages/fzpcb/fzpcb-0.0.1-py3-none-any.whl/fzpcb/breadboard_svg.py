from .coords import Size
from .grid_drawing import GridDrawing

def breadboard_svg(board, gridlines=False):
    # Draw breadboard SVG, returning it in ElementTree XML
    grid = GridDrawing(
        size=board.size, 
        border=Size(0.2, 0.2),
        grid_size=board.config['metadata']['grid_size'],
        grid_unit=board.config['metadata']['grid_unit'],
        scale=board.config['metadata']['scale'],
        parts_dict=board.config['breadboard-parts'])

    breadboard = grid.g(id='breadboard')
    
#     c2 = CoordsTo(grid.border, Position.zero(), self.scale)
#     # print(Outline(board.layout).path_d(c2, Vector(0.1, 0.1), Size(0.3, 0.3), Size(0.6, 0.6)))
#     
# 
#     # c2 = CoordsTo(grid.border, Size.zero(), self.scale)
#     # path_d = outline.path_d(c2, Size.zero(), Size(0.3, 0.3), Size(0.6, 0.6))
#     # grid.add(grid.path(stroke='black', fill='none', stroke_width=lw/10*self.scale, d=path_d))
    pcb_shape = grid.pcb_shape(board)
    breadboard.add(pcb_shape)

    font = board.config['appearance']['breadboard']['font']
    colour_dict = board.config['colours']
    
    for cell in board.parts:
        breadboard.add(grid.draw_part(cell, font, colour_dict))

    # print(board.layout.connectors)
    for cell in board.connectors.values():
        breadboard.add(grid.draw_part(cell, font, colour_dict))

    for cell in board.text.values():
        breadboard.add(grid.draw_text(cell, board.text_dict, colour_dict))

    grid.add(breadboard)

    if gridlines:
        grid.add(grid.grid_lines(*board.size))
        
    return grid.get_xml()
