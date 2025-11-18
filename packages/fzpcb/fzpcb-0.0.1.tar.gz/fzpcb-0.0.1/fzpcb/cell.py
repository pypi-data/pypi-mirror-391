from .array_2d import Member
from .coords import Size

class Cell(Member):
    def __init__(self, element):
        super().__init__()
        self.element = element
        
class EmptyCell(Cell):
    pass

class PCBCell(Cell):
    pass

class ConnectorCell(Cell):
    def __init__(self, element):
        # Caller only knows the connector number when created
        if not element.ispair():
            raise AssertionError('Must not call on processed/missing elements')
        self.number = int(element.char + element.right.char, base=10)
        super().__init__(element)
        self.colour_key =  None  # We don't know what kind of connector this is
        self.part_key = None # Board will parse that from connector descriptions
        self.size = Size(2, 2)
        self.schemed = None # Not yet positioned in schematic
        
    def update(self, colour_key, part_key, label, 
               description, gender, cid, part_ops=[]):
        # Caller uses update when all details of connector are known
        self.colour_key = colour_key # Gets
        self.part_key = part_key
        self.label = label
        self.description = description
        self.gender = gender
        self.cid = cid
        self.part_ops = part_ops
        
class PartCell(Cell):
    def __init__(self, element, size):
        if not element.ispair():
            raise AssertionError('Must not call on processed/missing elements')
        super().__init__(element)
        self.colour_key = element.char.upper()
        self.part_key = element.right.char
        self.size = size
        self.part_ops = []
                
class TextCell(Cell):
    def __init__(self, element):
        if not element.ispair():
            raise AssertionError('Must not call on processed/missing elements')
        super().__init__(element)
        self.text_marker = element.char
        self.text_key = element.char.upper() + element.right.char
        self.size = Size(2, 2)
# 
#     def __repr__(self):
#         if self.type == CellType.NONE:
#             return '     '
#         elif self.type == CellType.CONNECTOR:
#             return f'{self.number:02}{self.size.width}x{self.size.height}@{self.position.x},{self.position.y}'
#         elif self.type == CellType.PART:
#             return f'{self.colour_key}{self.part_key}{self.size.width}x{self.size.height}@{self.position.x},{self.position.y}'
#         elif self.type == CellType.TEXT:
#             return f'{self.text_key}{self.size.width}x{self.size.height}@{self.position.x},{self.position.y}'
#         elif self.type == CellType.PCB:
#             return f'PCB@{self.position.x},{self.position.y}'
#         elif self.type == CellType.NONE:
#             return f'None@{self.position.x},{self.position.y}'
#         else:
#             raise AssertionError("Can't happen")
#         
# 
