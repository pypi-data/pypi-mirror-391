#!/usr/bin/env python

from enum import Enum, auto #, IntFlag
from dataclasses import dataclass, astuple
# from math import atan2, cos, sin, pow, sqrt
from copy import copy

class Dir(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
#     
# class Edge(IntFlag):
#     NONE = 0
#     TOP = 1
#     BOTTOM = 2
#     LEFT = 4
#     # TOP_LEFT = 5
#     # BOTTOM_LEFT = 6
#     RIGHT = 8
#     # TOP_RIGHT = 9
#     # BOTTOM_RIGHT = 10
#     ALL = 15
#     
#     def flip(self):
#         # Returns new edge with left and right swapped
#         
#         # Edge will be immutable, so no need to copy
#         # This can probably be done faster, but who cares?
#         left = self & self.__class__.LEFT
#         self ^= left
#         right = self & self.__class__.RIGHT
#         self ^= right
#         if left:
#             self |= self.__class__.RIGHT
#         if right:
#             self |= self.__class__.LEFT
#         return self
#     
#     def flop(self):
#         # Returns new edge with top and bottom swapped
#         top = self & self.__class__.TOP
#         self ^= top
#         bottom = self & self.__class__.BOTTOM
#         self ^= bottom
#         if top:
#             self |= self.__class__.BOTTOM
#         if bottom:
#             self |= self.__class__.TOP
#         return self
#     
#     def chain(self, ops):
#         new = copy(self)
#         for op in ops:
#             new = op(new)
#         return new

class Coords:
    def __getitem__(self, item):
        return astuple(self)[item]
    
    # def __str__(self):
    #     # String reprsentation is just the two coords separated by a space,
    #     # as used by SVG in paths, viewboxes, etc
    #     # FIXME Not needed?
    #     return f'{self[0]} {self[1]}'
    
    def __mul__(self, multiplier):
        # print(f'{self}.__mul__({multiplier})')
        try:
            return self.__class__(self[0] * multiplier[0], self[1] * multiplier[1])
        except TypeError:
            return self.__class__(self[0] * multiplier, self[1] * multiplier)
        
    __rmul__ = __mul__
    
    def __truediv__(self, divisor):
        try:
            return self.__class__(self[0] / divisor[0], self[1] / divisor[1])
        except TypeError:
            return self.__class__(self[0] / divisor, self[1] / divisor)
        
    def __add__(self, other):
        # print(repr(self))
        # print(repr(other))
        try:
            return self.__class__(self[0] + other[0], self[1] + other[1])
        except TypeError:
            return self.__class__(self[0] + other, self[1] + other)
    
    def __sub__(self, other):
        try:
            return self.__class__(self[0] - other[0], self[1] - other[1])
        except TypeError:
            return self.__class__(self[0] - other, self[1] - other)

    def __neg__(self):
        return self.__class__(-self[0], -self[1])

    def __abs__(self):
        return self.__class__(abs(self[0]), abs(self[1]))
    
    def maxwith(self, other):
        try:
            return self.__class__(max(self[0], other[0]), max(self[1], other[1]))
        except TypeError:
            return self.__class__(max(self[0], other), max(self[1], other))
    
    def minwith(self, other):
        try:
            return self.__class__(min(self[0], other[0]), min(self[1], other[1]))
        except TypeError:
            return self.__class__(min(self[0], other), min(self[1], other))

    def across(self):
        # Only the x / width / dx coordinate
        return self.__class__(self[0], 0)
    
    def right(self):
        # Only the x / width / dx coordinate
        return self.__class__(self[0], 0)
    
    def left(self):
        # Only the y / height / dy coordinate, negated
        return -self.right()
    
    def down(self):
        # Only the y / height / dy coordinate
        return self.__class__(0, self[1])

    def up(self):
        # Only the y / height / dy coordinate, negated
        return -self.down()

    def flip(self):
        # Invert the x / width / dx coordinate
        return self.__class__(-self[0], self[1])

    def flop(self):
        # Invert the y / height / dy coordinate
        return self.__class__(self[0], -self[1])
    
    def flipflop(self):
        # Invert both coords. Same as __neg__
        return self.__class__(-self[0], -self[1])
    
    def identity(self):
        return self
    
    # flip and flop together can be done with -coord (or -1 * coord)
    
    def transpose(self):
        # Swap coordinates, transpose+flip and transpose+flop are rotations
        return self.__class__(self[1], self[0])

    def length(self):
        return sqrt(pow(self[0], 2) + pow(self[1], 2))
    
    def angle(self):
        return atan2(self[1], self[0])
    
    def point_on_ellipse(self, angle):
        # Give point 'angle' way around an ellipse with semi-axies of coords
        ab = self[0] * self[1]
        b_cos = self[1] * cos(angle)
        a_sin = self[0] * sin(angle)
        div = sqrt(pow(b_cos, 2) + pow(a_sin, 2))
        x = ab * cos(angle) / div
        y = ab * sin(angle) / div
        return self.__class__(x, y)
    
    def chain(self, ops):
        new = copy(self)
        for op in ops:
            new = new.__getattribute__(op)()
        return new

    def pchain(self, ops):
        new = copy(self)
        for op in ops:
            if op == 'transpose':
                new = new.__getattribute__(op)()
        return new

    def fchain(self, ops):
        new = self
        for op in ops:
            large_arc_flag = new[0]
            sweep_flag = abs(new[1] - 1)
            new = Vector(large_arc_flag, sweep_flag)
        return new


    # FIXME do we need/want rotations?
    
    @classmethod
    def zero(cls):
        return cls(0, 0)

    @classmethod
    def half(cls):
        return cls(0.5, 0.5)

    @classmethod
    def one(cls):
        return cls(1, 1)

    @classmethod
    def two(cls):
        return cls(2, 2)

@dataclass
class Position(Coords):
    x: float
    y: float

@dataclass
class Size(Coords):
    width: float
    height: float

@dataclass
class Vector(Coords):
    dx: float
    dy: float
    
# @dataclass
# class ArcFlags(Coords):
#     # SVG arc flags that understand what to do with flip and flop
#     large_arc_flag: int
#     sweep_flag: int
#             
#     def flip(self):
#         return self.__class__(self.large_arc_flag, int(not self.sweep_flag))
#     
#     mirror = flop = flip
#     
#     # def mirror(self):
#     #     return self
    
class CoordsTo:
    def __init__(self, border, cell_position, scale, part_size=None, ops=None, step=1):
        self.border = border
        self.cell_position = cell_position
        self.scale = scale
        self.step = step
        if part_size:
            self.part_size = part_size
        else:
            self.part_size = Size(1,1)
        if ops:
            self.ops = ops
        else:
            self.ops = []
        
    def offset(self, offset):
        new = copy(self)
        new.border += offset
        return new
    
    def __repr__(self):
        return f'{self.__class__.__name__}(border={self.border}, cell_position={self.cell_position}, scale={self.scale}, part_size={self.part_size})'
    
    def cabs(self, coords):
        cell_centre = (self.border + self.cell_position + Vector.half()) * self.scale
        offset_from_centre = coords - Vector.half()
        result = cell_centre + self.crel(offset_from_centre)
        # print('cabs', coords, '->', result / self.scale)
        return result
    
    def crel(self, coords):
        result = coords.chain(self.ops) * self.scale
        # print('crel', coords, '->', result / self.scale)
        return result
    
    def clen(self, length):
        return length * self.scale
    
    def sabs(self, coords):
        step_centre = (self.border + self.cell_position + Vector.half() * self.step) * self.scale
        offset_from_centre = (coords - Vector.half()) * self.step
        result = step_centre + self.crel(offset_from_centre)
        # print('sabs', coords, '->', result / self.scale)
        return result

    # def sabs(self, coords):
    #     result = self.cabs(coords * self.step)
    #     # print('cabs', coords, '->', result / self.scale)
    #     return result
    
    def srel(self, coords):
        result = self.crel(coords * self.step)
        # print('crel', coords, '->', result / self.scale)
        return result
    
    def slen(self, length):
        return self.clen(length * self.step)

    def pabs(self, coords):
        # print('coords', coords)
        part_size = self.part_size.pchain(self.ops)
        offset = Vector.one()
        # print('half', half)
        part_centre = (self.border + self.cell_position + offset) * self.scale
        # print('part_centre', part_centre / self.scale)
        offset_from_centre = coords * part_size - offset
        # print('offset_from_centre', offset_from_centre)
        # result = part_centre + self.prel(offset_from_centre)
        result = part_centre + offset_from_centre.chain(self.ops) * self.scale
        # print('pabs', coords, '->', coords * self.part_size, '->', result / self.scale)
        # print(self)
        return result
    
    def prel(self, coords):
        result = self.crel(coords * self.part_size.pchain(self.ops))
        # print('prel', coords, '->', coords * self.part_size, '->', result / self.scale)
        return result
    
    def prelh(self, coords):
        transposed_size = self.part_size.pchain(self.ops)
        part_size_h = Size(transposed_size[0], transposed_size[0])
        result = self.crel(coords * part_size_h.pchain(self.ops))
        # print('prel', coords, '->', coords * self.part_size, '->', result / self.scale)
        return result

    def prelv(self, coords):
        transposed_size = self.part_size.pchain(self.ops)
        part_size_v = Size(transposed_size[1], transposed_size[1])
        result = self.crel(coords * part_size_v.pchain(self.ops))
        # print('prel', coords, '->', coords * self.part_size, '->', result / self.scale)
        return result

    def parcsize(self, coords):
        result = self.crel(coords * self.part_size.pchain(self.ops))
        result = coords.__class__(abs(result[0]), abs(result[1]))
        # print('prel', coords, '->', coords * self.part_size, '->', result / self.scale)
        return result
    
    def transpose_only(self, coords):
        print(self.ops)
        result = coords.chain(self.ops)
        result = coords.__class__(abs(result[0]), abs(result[1]))
        # print('prel', coords, '->', coords * self.part_size, '->', result / self.scale)
        return result

    def parcflags(self, flags):
        return flags.fchain(self.ops)
    
    def plenh(self, length):
        return self.clen(length * self.part_size.pchain(self.ops)[0])
    
    def plenv(self, length):
        return self.clen(length * self.part_size.pchain(self.ops)[1])
    
    def plen(self, length):
        return self.clen(length * (self.part_size[0] + self.part_size[1])/2)
    
    def jump(self, coords):
        return self.crel(coords + (self.part_size - Vector.one()).pchain(self.ops))
    
    def jumpback(self, coords):
        return self.crel(coords - (self.part_size + Vector.one()).pchain(self.ops))
    
    def jumpright(self, coords):
        # print('A', coords)
        # print('B', self.part_size)
        # print('C', Vector(self.part_size[0]-1, 0))
        # print('D', coords + Vector(self.part_size[0]-1, 0).pchain(self.ops))
        return self.crel(coords + Vector(self.part_size.pchain(self.ops)[0]-1, 0))
    
    def jumpdown(self, coords):
        return self.crel(coords + Vector(0, self.part_size.pchain(self.ops)[1]-1))
    
    def jumpleft(self, coords):
        return self.crel(coords - Vector(self.part_size.pchain(self.ops)[0]-1, 0))
    
    def jumpup(self, coords):
        return self.crel(coords - Vector(0, self.part_size.pchain(self.ops)[1]-1))
    
    def f(self, arc_flags):
        # FIXME What happens if self.ops are subclassed from Coords.flip, etc.
        # but coords is an ArcFlag
        return arc_flags.chain(self.ops)
    
    # def chain(self, ops):
    #     # Apply ops to coord
    #     new = copy(self)
    #     for op in ops:
    #         new = op(new)
    #     return new
#         
#     def pchain(self, ops):
#         # Only apply transpose to coord, necessary to recalc partsize
#         new = copy(self)
#         for op in ops:
#             if op == 'transpose':
#                 new = op(new)
#         return new
        
    def expand_args_list(self, args_list):
        # Convert list of part functions arguments to real-world coordinates
        
        one_arg_funcs = ['clen', 'slen', 'plenh', 'plenv', 'plen']
        two_arg_funcs = ['pabs', 'prel', 'prelh', 'prelv', 'parcsize', 'parcflags', 'cabs', 'crel', 'sabs', 'srel', 'jump', 'jumpback', 'jumpright', 'jumpdown', 'jumpleft', 'jumpup']
        result = []
        seven_arg_funcs = ['parc'] #, 'pcirc']
        
        for arg in args_list:
            if isinstance(arg, dict):
                if len(arg) != 1:
                    raise ValueError(f'Part function maps must have only one key: {arg}')
                
                for func, func_args in arg.items(): # There is only one, Highlander
                    if func in one_arg_funcs:
                        if len(func_args) != 1:
                            raise ValueError(f'Part function {func} expects 1 argument: {arg}')
                    elif func in two_arg_funcs:
                        if len(func_args) != 2:
                            raise ValueError(f'Part function {func} expects 2 arguments: {arg}')
                    elif func in seven_arg_funcs:
                        if len(func_args) != 7:
                            raise ValueError(f'Part function {func} expects 7 arguments: {arg}')
                    else:
                        raise ValueError(f'Unrecognzed part function: {func}')

                    if func == 'clen':
                        result.append(self.clen(*func_args))
                    elif func == 'slen':
                        result.append(self.slen(*func_args))
                    elif func == 'plenh':
                        result.append(self.plenh(*func_args))
                    elif func == 'plenv':
                        result.append(self.plenv(*func_args))
                    elif func == 'plen':
                        result.append(self.plen(*func_args))
                    elif func == 'pabs':
                        result.extend(self.pabs(Vector(*func_args)))
                    elif func == 'prel':
                        result.extend(self.prel(Vector(*func_args)))
                    elif func == 'prelh':
                        result.extend(self.prelh(Vector(*func_args)))
                    elif func == 'prelv':
                        result.extend(self.prelv(Vector(*func_args)))
                    elif func == 'parcsize':
                        result.extend(self.parcsize(Vector(*func_args)))
                    elif func == 'parcflags':
                        result.extend(self.parcflags(Vector(*func_args)))
                    elif func == 'parc':
                        result.extend([
                            *self.parcsize(Vector(func_args[0], func_args[1])),
                            func_args[2],
                            *self.parcflags(Vector(func_args[3], func_args[4])),
                            *self.prel(Vector(func_args[5], func_args[6]))])
                    # elif func == 'pcirc':
                    #     avg = func_args[0] + func_args[1] / 2
                    #     result.extend([
                    #         *self.parcsize(Vector(avg, avg)),
                    #         func_args[2],
                    #         *self.parcflags(Vector(func_args[3], func_args[4])),
                    #         *self.prel(Vector(func_args[5], func_args[6]))])
                    elif func == 'cabs':
                        result.extend(self.cabs(Vector(*func_args)))
                    elif func == 'crel':
                        result.extend(self.crel(Vector(*func_args)))
                    elif func == 'sabs':
                        result.extend(self.sabs(Vector(*func_args)))
                    elif func == 'srel':
                        result.extend(self.srel(Vector(*func_args)))
                    elif func == 'jump':
                        result.extend(self.jump(Vector(*func_args)))
                    elif func == 'jumpleft':
                        result.extend(self.jumpleft(Vector(*func_args)))
                    elif func == 'jumpright':
                        result.extend(self.jumpright(Vector(*func_args)))
                    elif func == 'jumpup':
                        result.extend(self.jumpup(Vector(*func_args)))
                    elif func == 'jumpdown':
                        result.extend(self.jumpdown(Vector(*func_args)))
                    else:
                        raise AssertionError("Can't happen")
                            
            elif isinstance(arg, (str, float, int)):
                result.append(arg)
            else:
                raise ValueError(f'Part args can only be dict, str, float, or int: "{arg}"')
        return result

if __name__ == '__main__':
    position = Position(0.2, 0.3)
    print(f'position = {position}')
    print(f'position with str = {str(position)}')
    print(f'position with repr = {repr(position)}')
    vector = Vector(3, 4)
    print(f'vector = {vector}')
    scale = Size(10, 20)
    print(f'scale = {scale}')
    
    c2 = CoordsTo(Size(1, 1), Position(2, 3), Size(10, 10))
    print(f'c2.a(position) = {c2.a(position)}')
    print(f'c2.r(position) = {c2.r(position)}')

    edges = Edge.LEFT | Edge.TOP
    print(edges)
    print(edges.flip())
    print(edges.flip().flop())
    
    print()
    print('Testing chain')
    print(edges)
    ops = [Edge.flip, Edge.flop]
    print(edges.chain(ops))
    
    sf = SweepFlag(2)
    print(sf)
    print(sf.flip())
    print(sf.flip().flop())
    
