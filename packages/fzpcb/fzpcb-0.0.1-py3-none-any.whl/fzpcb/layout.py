#!/usr/bin/env python

from enum import Enum, auto
from copy import deepcopy

from .array_2d import Array2D
from .cell import Cell, ConnectorCell, TextCell, PartCell, PCBCell, EmptyCell
from .element import Element
from .coords import Vector, Size

class Layout(Array2D):
    # 2D array of cells, which can each be none, a part or a connector
    # Built from list of strings showing PCB layout
    # Layout[y][x] references the cell at a given position
    # Other attibutes are:
    #   source:     2D array of source characters (used to draw PCB outline)
    #   size:       the layout size
    #   connectors: dict of connectors. indexed by number
    #   parts:      list of parts
    
    def __init__(self, source, empty_char, pcb_chars, text_chars,
                 top, middle, half_bottom):
        # We remove from this, as cells are indentified
        
        # for row in source:
        #     for element in row:
        #         print(f'Element {element}')        # Remove stuff not part of the PCB
        # for element in source.flatten():
        #     if element.char == empty_char:
        #         element.remove()

        # This copy we keep, as a record of the PCB shape
        # self.source = deepcopy(source)
        
        # # Layout is twice as high as source, and last row could be offset down
        # initializer = []
        # for _ in range(source.size.height * 2):
        #     initializer.append([Cell() for _ in range(source.size.width)])
        # super().__init__(initializer)
        
        # Remove stuff in the PCB that isn't a connector, part, or text
        # for element in source.flatten():
        #     if element.char and element.char in pcb_chars:
        #         cell = self.obj_by_pos(element.layout_position())
        #         cell.make_pcb(element)
        #         element.remove()
            
        cell_rows = []
        for row in source:
            cell_upper_row = []
            cell_lower_row = []
            for element in row:
                # print(f'Checking element {element}')
                if element.char == empty_char:
                    cell_upper_row.append(EmptyCell(element))
                    cell_lower_row.append(EmptyCell(element))
                    element.processed = True
                elif element.processed or element.char in pcb_chars:
                    cell_upper_row.append(PCBCell(element))
                    cell_lower_row.append(PCBCell(element))
                    element.processed = True
                elif element.right and not element.right.char in pcb_chars:
                    # Find connectors
                    try:
                        cell = ConnectorCell(element)
                        cell_upper_row.append(cell)
                        cell_lower_row.append(PCBCell(element))
                    except ValueError:
                        # Must be text or part
                        # Part extenders from higher parts will have been processed
                        if element.char.upper() in text_chars:
                            cell = TextCell(element)
                        else:
                            # get_part_size() marks extenders as processed
                            size = element.get_part_size(top, middle, half_bottom)
                            cell = PartCell(element, size)
                            
                        if element.char.isupper():
                            cell_upper_row.append(cell)
                            cell_lower_row.append(PCBCell(element))
                        else:
                            cell_upper_row.append(PCBCell(element))
                            cell_lower_row.append(cell)
                            
                    element.processed = True
                    element.right.processed = True                        
                else:
                    raise ValueError(f'Unexpected character {element.char} at {element.position}')
            cell_rows.append(cell_upper_row)
            cell_rows.append(cell_lower_row)
        
        # print(cell_rows)
        
        super().__init__(cell_rows)

    def __str__(self):
        rows = []
        for row in self:
            rows.append('|'.join(str(c) for c in row))
        return '\n'.join(rows)
        
        
if __name__ == '__main__':
    source = [
        '.Aa+.', 
        'Ca+..', 
        '###..', 
        '.bB..',
        '.##ff']
    layout = Layout(source, ' ', '.', '+', '#', '=')
    print(layout)
   
