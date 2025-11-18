from copy import copy
from collections import OrderedDict

from .colour_list import ColourList
from .layout import Layout
from .coords import Position, Size
from .helpers import find_colour_from_key, merge_subdicts_with_defaults
from .array_2d import Array2D
from .element import Element
from .cell import ConnectorCell, PartCell, TextCell

class Board():
    # Convert into the format we work with
    def __init__(self, config):
        self.config = config

        # Turn colour strings into ColoursLists
        # print(self.config['colours'])
        new_colour_dict = {}
        for colour_code, sequence in self.config['colours'].items():
            # print(f'{colour_code} mapped to {sequence}')
            colour_list = ColourList(sequence)
            try:
                colour_letter, colour_word = colour_code.split('+', maxsplit=1)
            except ValueError:
                new_colour_dict[colour_code] = colour_list
            else:
                new_colour_dict[colour_letter] = colour_list
                new_colour_dict[colour_word] = colour_list
        self.config['colours'] = new_colour_dict
        # for k, v in self.config['colours'].items():
        #     try:
        #         print(k, repr(v))
        #     except TypeError:
        #         print(f"Can't print {k}")
        # print(self.config['colours']['pcb'])
        
        # Extract colour_codes that indicate text
        text_chars = []
        for letter, colour_list in config['colours'].items():
            if colour_list.istext():
                text_chars.append(letter)
                
        self.source = Array2D([Element.from_str(s) for s in config['layout']])
        # Unlink empty cells, so outline of PCB can be traced
        for element in self.source.flatten():
            if element.char == config['specials']['empty']:
                element.unlink()

        self.layout = Layout(self.source, 
                             config['specials']['empty'],
                             config['specials']['pcb'],
                             text_chars,
                             config['extenders']['top'],
                             config['extenders']['middle'],
                             config['extenders']['half-bottom'])

        # Find the connector cells, and put them in a ordered dict
        connectors = {}
        for cell in self.layout.flatten():
            if isinstance(cell, ConnectorCell):
                if cell.number in connectors:
                    raise ValueError(f'Duplicate connector {cell.number} at position {cell.element.position.x},{cell.element.position.y}')
                else:
                    connectors[cell.number] = cell
        self.connectors = OrderedDict()
        for cell in [connectors[key] for key in sorted(connectors.keys())]:
            self.connectors[cell.number] = cell

        # for number, (key, connector) in enumerate(self.connectors.items()):
        #     print(number, key, connector)
        
        # Find the part cells, and put them in a list
        self.parts = []
        for cell in self.layout.flatten():
            if isinstance(cell, PartCell):
                self.parts.append(cell)

        # Find the text cells, and put them in a dict
        self.text = {}
        for cell in self.layout.flatten():
            if isinstance(cell, TextCell):
                if cell.text_key in self.text:
                    raise ValueError(f'Duplicate text {cell.text_key} at position {cell.element.position.x},{cell.element.position.y}')
                else:
                    self.text[cell.text_key] = cell

        # Apply defaults to connector dicts, and merge them
        connector_defaults = config['connectors']['defaults']
        connector_dict = merge_subdicts_with_defaults(config, 'connector')
         
        # Take the connector dict values, and use them to update the
        # connector cell
        for cid, cell in enumerate(self.connectors.values()):
            try:
                connector = connector_dict[cell.number]
            except KeyError:
                connector = connector_defaults
            self.update_connector(cid, cell, connector)
            
        # Find connectors with the same name and put them in buses
        conn_by_label = {}
        for cell in self.connectors.values():
            try:
                conn_by_label[cell.label].append(cell)
            except KeyError:
                conn_by_label[cell.label] = [cell]
        self.buses = {}
        for label, cell_list in conn_by_label.items():
            if len(cell_list) > 1:
                self.buses[label] = cell_list
        
        # Apply defaults to text dicts, and merge them
        self.text_dict = merge_subdicts_with_defaults(config, 'text')
                
        # Add undefined text keys to the text dict
        for cell in self.text.values():
            if cell.text_key not in self.text_dict:
                self.text_dict[cell.text_key] = config['text']['defaults']
                self.text_dict[cell.text_key]['text'] = f'Text-{cell.text_key}-undefined'

        self.size = self.layout.size
        # print(self.text_dict)

    @staticmethod
    def update_connector(cid, cell, connector):
        # Update the a cell with connector details, now we know them
        colour_key = connector['colour']
        gender = connector['gender']

        try:
            text = connector['text']
        except KeyError:
            text = f'PIN{cell.number} Connector {cell.number}'

        pair = text.split(' ', maxsplit=1)
        
        try:
            label = connector['label']
        except KeyError:
            try:
                label = pair[0]
            except IndexError:
                label = ''

        try:
            description = connector['description']
        except KeyError:
            try:
                description = pair[1]
            except IndexError:
                description = ''

        # Work out if it is an edge connector, and of so, what the operations
        # to perform to rotate the part correctly
        # NOTE Only elements are unlinked if empty, not cells
        part_ops = []
        edge = False
        if not cell.element.left:
            part_ops = []
            edge = True
        elif not cell.element.right or not cell.element.right.right:
            part_ops = ['flip']
            edge = True
        elif not cell.element.up:
            part_ops = ['transpose']
            edge = True
        elif not cell.element.down:
            part_ops = ['transpose', 'flop']
            edge = True

        # Work out what possible parts to use
        if label == 'GND':
            if edge:
                possible = ['gnd-edge-part', 'gnd-part', 'edge-part', 'part']
            else:
                possible = ['gnd-part', 'part']
        else:
            if edge:
                possible = ['edge-part', 'part']
            else:
                possible = ['part']

        # And pick the first one that matches:
        for part_key_name in possible:
            if part_key_name in connector:
                part_key = connector[part_key_name]
                break
        else:
            raise ValueError('Connectors must have a (possible default) part')
                            
        cell.update(colour_key, part_key, label, 
                                description, gender, cid, part_ops)


    def colour(self, colour_key, default_key='unknown'):
        # Helper function to find colour
        return find_colour_from_key(self.config['colours'], colour_key, default_key)
