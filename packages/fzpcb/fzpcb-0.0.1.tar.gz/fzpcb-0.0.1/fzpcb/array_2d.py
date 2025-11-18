#!/usr/bin/env python
import itertools

from .coords import Position, Size

class Member():
    # Member of a 2D array that knows its position and neighbours
    # Expected to be sub-classed
    
    def __init__(self):
        self.position = None
        self.array_1d = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
    
    def __str__(self):
        up = (self.up.atstr() if self.up else 'nul')
        down = (self.down.atstr() if self.down else 'nul')
        left = (self.left.atstr() if self.left else 'nul')
        right = (self.right.atstr() if self.right else 'nul')
        return f'@{self.atstr()} <{left} ^{up} v{down} >{right}'
    
    def atstr(self):
        return f'{self.position.x},{self.position.y}'
        
    def unlink(self):
        if self.up:
            # print(f'Unlink from {self.up.atstr()}')
            self.up.down = None
            self.up = None
        if self.down:
            # print(f'Unlink from {self.down.atstr()}')
            self.down.up = None
            self.down = None
        if self.left:
            # print(f'Unlink from {self.left.atstr()}')
            self.left.right = None
            self.left = None
        if self.right:
            # print(f'Unlink from {self.right.atstr()}')
            self.right.left = None
            self.right = None
    
    # FIXME Would be nice to have swap(self, other), but links get tricky
    # when swapping neighbours
    def swap_below(self):
        if not self.down:
            raise AssertionError(f'Can swap member @{self.atstr()} with one below')
        
        other = self.down
        
        # Swap attributes
        for attr in ['position', 'array_1d', 'up', 'down', 'left', 'right']:
            save = getattr(self, attr)
            setattr(self, attr, getattr(other, attr))
            setattr(other, attr, save)

        # Fix what we broke
        self.up = other
        other.down = self

        # Introduce ourselves to our new neighbours
        self.update_neighbours()
        other.update_neighbours()
          
        # Swap in parent 1D arrays
        self.array_1d[self.position.x] = self
        other.array_1d[other.position.x] = other
        
    # Iterators through the 2D array
    
    def update_neighbours(self):
        if self.up:
            self.up.down = self
        if self.down:
            self.down.up = self
        if self.left:
            self.left.right = self
        if self.right:
            self.right.left = self
        
    def iter_up(self):
        while self:
            yield self
            self = self.up

    def iter_down(self):
        while self:
            yield self
            self = self.down

    def iter_left(self):
        while self:
            yield self
            self = self.left

    def iter_right(self):
        while self:
            yield self
            self = self.right

class Array1D(list):
    def __init__(self, array_2d, y, row):
        self.array_2d = array_2d
        self.y = y
        super().__init__(row)
        
        for x, member in enumerate(row):
            member.position = Position(x, y)
            member.array_1d = self
            
class Array2D(list):
    # 2D array that must be initialized all in one go (no appending/extending)
    def __init__(self, rows):
        super().__init__(Array1D(self, y, row) for y, row in enumerate(rows))
        
        # Set member left and right links
        for row in self:
            for left, right in zip(row, row[1:]):
                left.right = right
                right.left = left
                
        # Set member up and down links
        for row_above, row_below in zip(self, self[1:]):
            for up, down in zip(row_above, row_below):
                up.down = down
                down.up = up

        self.size = Size(len(max(self, key=len)), len(self))
        
    def flatten(self):
        # Convenience function to process all members with one iterator
        return itertools.chain.from_iterable(self)
    
    def member_at(self, position):
        # Convenience function to index with coordinate tuple
        return self[position[1]][position[0]]
    
if __name__ == '__main__':
    class T(Member):
        def __init__(self, value):
            self.value=value
            super().__init__()
        def __repr__(self):
            return self.value + super().__str__()
        
    array = Array2D([[T('a'), T('b')], [T('c'), T('d'), T('e')], [T('f'), T('g'), T('h')], [T('i'), T('j'), T('k')]])
    for row in array:
        print(row)
        
    array[1][1].swap_below()
    print()
    for row in array:
        print(row)
    print(array.size)
        
    array[1][1].swap_below()
    print()
    for row in array:
        print(row)
    print(array.size)

    array[0][0].swap_below()
    print()
    for row in array:
        print(row)
    print(array.size)
        
    array[0][0].swap_below()
    print()
    for row in array:
        print(row)
    print(array.size)

    array[1][1].unlink()
    print()
    for row in array:
        print(row)
    print(array.size)
