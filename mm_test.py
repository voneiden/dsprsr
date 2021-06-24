import json

from utils.magic_mapper import Value, List, Schema, magic_map


def test():
    with open('data/atpack/ATtiny814.atdf.json', 'r') as f:
        atdf = json.load(f)

    root = Value('avr-tools-device-file')
    devices = root >> Value('devices') >> List('device', cast=True, min_length=1, max_length=1)
    device_modules = Value('peripherals') >> List('module', cast=True, min_length=1, max_length=1)
    module_instances = List('instance', cast=True, min_length=1, max_length=1)
    instance_signals = Value('signals') >> List('signal', cast=True, min_length=1, max_length=1)

    signal_schema = Schema({
        'function': Value('@function'),
        'group': Value('@group'),
        'index': Value('@index'),
        'pad': Value('@pad'),
    })

    instance_schema = Schema({
        'signals': instance_signals >> signal_schema
    })

    module_schema = Schema({
        'instances': module_instances >> instance_schema
    })

    device_schema = Schema({
        'name': Value('@name'),
        'modules': device_modules >> module_schema
    })

    schema = {
        'devices': devices >> device_schema
    }
    return magic_map(schema, atdf)


if __name__ == '__main__':
    test()
