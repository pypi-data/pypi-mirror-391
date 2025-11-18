#!/usr/bin/env python
from copy import copy, deepcopy
from colour import Color as Colour
 
class ColourList:
    # Either a text marker, or a list of colours, with "none" as an allowable colour.
    # Once colour lists are created, they are not expected to change.
    # Stringized version of colours are designed to be used in SVG documents, which
    # is why "none" is added to what colour supports natively.
    # Text markers (create by passing the literal "text") are a bit of a hack, to
    # allow fritizingpcb to use the same character to designate a cell to be either a
    # part with a colour, or a text string (the value of which is defined elsewhere
    # in the input YAML).
 
    def __init__(self, sequence):
        if not sequence:
            raise ValueError('ColourList must be initiated with a value')
 
        # print(type(sequence), sequence)
        self.text = False
        self.data = []
 
        if isinstance(sequence, str):
            sequence = [s.strip() for s in sequence.split(',')]
 
        if sequence[0] == 'text':
            self.text = True
            return

        for element in sequence:
            if element != 'none':
                self.data.append(Colour(element))
            else:
                self.data.append('none')
 
        if len(self.data) < 2:
            self.data.append(deepcopy(self.data[0]))
            if self.data[1] != 'none':
                try:
                    self.data[1].luminance -= 0.1
                    # Out-of-bounds luminance is not raised until colour is evaluated
                    # so force an evaluation to trigger ValueError
                    str(self.data[1])
                except ValueError:
                    self.data[1].luminance = 0
 
        if len(self.data) < 3:
            self.data.append(deepcopy(self.data[0]))
            if self.data[2] != 'none':
                try:
                    self.data[2].luminance += 0.1
                    str(self.data[2])
                except ValueError:
                    self.data[2].luminance = 1
 
    def __getitem__(self, item):
        if self.text:
            raise TypeError('Cannot index text marker')
        else:
            return self.data[item]
 
    def __str__(self):
        if self.text:
            raise TypeError('Cannot stringize text marker')
        return str(self.data[0])
 
    def __repr__(self):
        if self.text:
            return f'{self.__class__.__name__}("text")'
        else:
            datastr = ', '.join('"'+str(c)+'"' for c in self.data)
            return f'{self.__class__.__name__}([{datastr}])'
 
    def istext(self):
        return self.text
 
if __name__ == '__main__':
    x = 'none'
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
    x = 'text'
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
   
    x = 'blue'
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
   
    x = 'white'
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
 
    x = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
 
 
    x = 'red, green,blue ,yellow, cyan, none, magenta'
    print(f'\nTrying {x}')
    c = ColourList(x)
    if not c.istext():
        print(c, c[0], c[1], c[2])
    print(repr(c))
