import xml.etree.ElementTree as ET

def fzp_filename(real_filename):
    (svg, dirname, filename) = real_filename.split('.', maxsplit=2)
    return f'{dirname}/{filename}'

def fzp_xml(board, input_filename, schematic_filename, pcb_filename, breadboard_filename):
    # Build Fritzing metadata, returning it in ElementTree XML
    
    schematic_filename = fzp_filename(schematic_filename)
    pcb_filename = fzp_filename(pcb_filename)
    breadboard_filename = fzp_filename(breadboard_filename)

    metadata =  board.config['metadata']
    fzp = ET.Element('module',
                        referenceFile=input_filename,
                        moduleId=metadata['SVGbasename'],
                        fritzingVersion='0.3.16b.02.24.4002')

    ET.SubElement(fzp, 'author').text = metadata['author']
    ET.SubElement(fzp, 'version').text = metadata['version']
    ET.SubElement(fzp, 'title').text = metadata['title']
    ET.SubElement(fzp, 'url').text = metadata['url']
    ET.SubElement(fzp, 'label').text = metadata['label']
    ET.SubElement(fzp, 'date').text = metadata['date']
    ET.SubElement(fzp, 'description').text = metadata['description']
    
    tag_list = ET.SubElement(fzp, 'tags')
    for tag in board.config['tags']:
        ET.SubElement(tag_list, 'tag').text = tag
        
    property_list = ET.SubElement(fzp, 'properties')
    for name, value in board.config['properties'].items():
        # print(key)
        ET.SubElement(property_list, 'property', name=name).text = value
        
    view_list = ET.SubElement(fzp, 'views')
    
    view_element = ET.SubElement(view_list, 'iconView')
    layer_list = ET.SubElement(view_element, "layers", image=breadboard_filename)
    ET.SubElement(layer_list, 'layer', layerId='icon')

    view_element = ET.SubElement(view_list, 'breadboardView')
    layer_list = ET.SubElement(view_element, "layers", image=breadboard_filename)
    ET.SubElement(layer_list, 'layer', layerId='breadboard')
    
    view_element = ET.SubElement(view_list, 'schematicView')
    layer_list = ET.SubElement(view_element, "layers", image=schematic_filename)
    ET.SubElement(layer_list, 'layer', layerId='schematic')
    
    view_element = ET.SubElement(view_list, 'pcbView')
    layer_list = ET.SubElement(view_element, "layers", image=pcb_filename)
    ET.SubElement(layer_list, 'layer', layerId='copper0')
    ET.SubElement(layer_list, 'layer', layerId='copper1')
    ET.SubElement(layer_list, 'layer', layerId='silkscreen')
    
    connector_list = ET.SubElement(fzp, "connectors")
    for cid, connector in enumerate(board.connectors.values()):
        connector_element = ET.SubElement(
            connector_list,
            'connector',
            type=connector.gender,
            name=f'pin {connector.number}',
            id=f'connector{cid}')
        
        if connector.description:
            text = f'{connector.label} {connector.description}'
        else:
            text = f'{connector.label}'
        ET.SubElement(connector_element, 'description').text = text
        
        view_list = ET.SubElement(connector_element, 'views')
        
        view_element = ET.SubElement(view_list, 'breadboardView')
        ET.SubElement(
            view_element, 'p',
            svgId=f'connector{cid}pin',
            layer='breadboard')
        
        view_element = ET.SubElement(view_list, 'schematicView')
        ET.SubElement(
            view_element, 'p',
            svgId=f'connector{cid}pin',
            layer='schematic',
            terminalId=f'connector{cid}terminal')
        
        view_element = ET.SubElement(view_list, 'pcbView')
        ET.SubElement(
            view_element, 'p',
            svgId=f'connector{cid}pin',
            layer='copper0')
        ET.SubElement(
            view_element, 'p',
            svgId=f'connector{cid}pin',
            layer='copper1')
        
    bus_list = ET.SubElement(fzp, "buses")
    for bus_name, cell_list in board.buses.items():
        bus_element = ET.SubElement(bus_list, 'bus', id=bus_name)
        for cell in cell_list:
            ET.SubElement(
                bus_element, 'nodeMember',
                connectorId=f'connector{cell.cid}')
        
    ET.SubElement(fzp, "schematic-subparts")
    ET.SubElement(fzp, "spice")
    
    return fzp
