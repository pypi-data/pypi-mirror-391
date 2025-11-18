from .coords import Size
from .grid_drawing import GridDrawing

def pcb_svg(board, gridlines=False):
    # Draw PCN SVG, returning it in ElementTree XML
    grid = GridDrawing(
        size=board.size, 
        border=Size(0.2, 0.2),
        grid_size=board.config['metadata']['grid_size'],
        grid_unit=board.config['metadata']['grid_unit'],
        scale=board.config['metadata']['scale'],
        parts_dict=board.config['pcb-parts'])

    
#     c2 = CoordsTo(grid.border, Position.zero(), self.scale)
#     # print(Outline(board.layout).path_d(c2, Vector(0.1, 0.1), Size(0.3, 0.3), Size(0.6, 0.6)))
#     
# 
#     # c2 = CoordsTo(grid.border, Size.zero(), self.scale)
#     # path_d = outline.path_d(c2, Size.zero(), Size(0.3, 0.3), Size(0.6, 0.6))
#     # grid.add(grid.path(stroke='black', fill='none', stroke_width=lw/10*self.scale, d=path_d))
    silkscreen = grid.g(id='silkscreen')
    pcb_shape = grid.pcb_outline(board)
    silkscreen.add(pcb_shape)
    grid.add(silkscreen)

    copper1 = grid.g(id='copper1')
    copper0 = grid.g(id='copper0')

    font = board.config['appearance']['pcb']['font']
    colours = board.config['colours']
    
    for cell in board.connectors.values():
        copper0.add(grid.draw_part(cell, font, colours))

    # pcb.add(grid.grid_lines(*board.size))
    copper1.add(copper0)
    grid.add(copper1)

    if gridlines:
        grid.add(grid.grid_lines(*board.size))

    return grid.get_xml()
