from .array_2d import Member
from .coords import Size

class Element(Member):
    # Character that expects to be in an Array2D representing the original source
    def __init__(self, char):
        if not isinstance(char, str) or len(char) != 1:
            raise TypeError('Elements must be initialized with a str of length 1')
        self.char = char
        self.processed = False
        super().__init__()
            
    @classmethod
    def from_str(cls, string):
        # Helper function to make list of characters from a string
        return [cls(letter) for letter in string]
                
    def ispair(self):
        return not self.processed and self.right and not self.right.processed
    
    def row_processed(self, width, should_be):
        # Mark elements to the right processed, but only if they are should_be
        # print(f'Setting {width} elements to processed if they are {should_be}')
        for _ in range(width):
            if not self:
                raise ValueError('Went off end of row trying to mark it processed')
                break
            # print(f'  Checking to see if {self.char} matches')
            if self.char == should_be:
                # print(f'  Setting {self} to processed')
                self.processed = True
            self = self.right
    
    def __str__(self):
        if self.up:
            up = f'^{self.up.position.x},{self.up.position.y}'
        else:
            up = '^None'
        if self.down:
            down = f'v{self.down.position.x},{self.down.position.y}'
        else:
            down = 'vNone'
        if self.left:
            left = f'<{self.left.position.x},{self.left.position.y}'
        else:
            left = '<None'
        if self.right:
            right = f'>{self.right.position.x},{self.right.position.y}'
        else:
            right = '>None'
            
        return f'"{str(self.char)}"@{self.atstr()} {up} {down} {left} {right})'
    
    def get_part_size(self, top, middle, half_bottom):
        # Find the size of a part that has been extended with
        # special extender characters. Mark the extenders we use as processed
         
        if not self.ispair():
            raise AssertionError('Must not call on processed/missing elements')
        width = 2
        height = 2
        
        # Find length of top row of part
        this = self.right.right
        while this and not this.processed and this.char == top:
            width += 1
            this = this.right
        
        # Mark top row processed (but not the part pair itself)
        if width > 2:
            self.right.right.row_processed(width - 2, top)
        
        # Find height of part left size, marking rows processed as we go
        this = self.down
        while this and not this.processed and this.char == middle:
            height += 2
            next_down = this.down
            this.row_processed(width, middle)
            this = next_down
        
        # Find if we have an extra 1-high half-bottom, and mark it processed
        if this and not this.processed and this.char == half_bottom:
            height += 1
            this.row_processed(width, half_bottom)

        # print(Size(width, height))
        return Size(width, height)
