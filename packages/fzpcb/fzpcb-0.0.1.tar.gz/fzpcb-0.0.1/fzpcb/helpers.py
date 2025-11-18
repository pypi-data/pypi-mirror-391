from copy import copy

def find_colour_from_key(colour_dict, colour_key, default_key='unknown'):
    # Given a colour dict and a key, find the color
    # colour_key may be a tuple/list of key and index, in which case
    # return that specific colour, not the first
    if isinstance(colour_key, (tuple, list)):
        index = colour_key[1]
        colour_key = colour_key[0]
    else:
        index = 0

    if colour_key == '?':
        colour_key = default_key
        
    try:
        colour = colour_dict[colour_key]
    except KeyError:
        colour = colour_dict['unknown']

    return colour if index == 0 else colour[index]

def find_part_code_from_key(parts_dict, part_key):
    # Given a part code dict and a key, find the part code
    # Can be copies or transposed copies of other parts
    part_ops = []
    try:
        part_code = parts_dict[part_key]
        try:
            transpose_of = part_code['transpose']
            try:
                name = parts_dict[part_key]['name']
                part_code = parts_dict[transpose_of]
                part_code['name'] = name
            except KeyError:
                raise ValueError(f'Part {part_key} tried to transpose non-existant part {transpose_of}')
            part_ops.append('transpose')
        except KeyError:
            pass
            
        try:
            # Copy beats transpose, for no particular reason
            copy_of = part_code['copy']
            try:
                name = parts_dict[part_key]['name']
                part_code = parts_dict[copy_of]
                part_code['name'] = name
            except KeyError:
                raise ValueError(f'Part {part_key} tried to copy non-existant part {copy_of}')
        except KeyError:
            pass

    except KeyError:
        part_code = None # Special drawing code for this case
        
    return part_code, part_ops

def merge_subdicts_with_defaults(parent, starts_with, key_for_strings='text'):
    # Merge subdicts in parent that have a key starting with starts_with
    merge_dict_names = [k for k in parent.keys() if k.startswith(starts_with)]
    result = {}
    for merge_dict_name in merge_dict_names:
        merge_dict = parent[merge_dict_name]
        try:
            defaults = merge_dict['defaults']
        except KeyError:
            print(merge_dict_name)
            print(merge_dict)
            raise ValueError(f'Dictionary {merge_dict_name} needs a "defaults" key')
        for key, value in merge_dict.items():
            if key == 'defaults':
                continue
            if not isinstance(value, dict):
                text = str(value)
                value = copy(defaults)
                value[key_for_strings] = text
            for def_key, def_value in defaults.items():
                if def_key not in value:
                    value[def_key] = def_value
            result[key] = value
        del(parent[merge_dict_name])
    return result
