import re

from utils.magic_mapper import Value, List, Schema, magic_map


class BaseParser:
    table_signatures = []
    module_signature = []

    def __init__(self, atdf_json, datasheet_json):
        self.output = self.atdf_map(atdf_json)
        self.datasheet_json = datasheet_json

    def atdf_map(self, atdf_json):
        root = Value('avr-tools-device-file')

        # Device paths and schema
        devices = root >> Value('devices') >> List('device', cast=True, min_length=1, max_length=1)
        device_modules = Value('peripherals') >> List('module', cast=True, min_length=1)
        module_instances = List('instance', cast=True, min_length=1) # Should I reduce these? PORTA PORTB?
        instance_signals = Value('signals', default=None) >> List('signal', cast=True, min_length=1)

        signal_schema = Schema({
            'function': Value('@function'),
            'group': Value('@group'),
            'index': Value('@index', default=None),
            'pad': Value('@pad'),
        })

        instance_schema = Schema({
            'name': Value('@name'),
            'signals': instance_signals >> signal_schema
        })

        module_schema = Schema({
            'name': Value('@name'),
            'instances': module_instances >> instance_schema
        })

        device_schema = Schema({
            'name': Value('@name'),
            'modules': device_modules >> module_schema
        })

        # Pinout paths and schema
        pinouts = root >> Value('pinouts') >> List('pinout', cast=True, min_length=1, max_length=1)

        pin_schema = Schema({
            'pad': Value('@pad'),
            'position': Value('@position')
        })

        pinout_schema = Schema({
            'name': Value('@name'),
            'pins': List('pin') >> pin_schema
        })

        # Module paths and schema
        modules = root >> Value("modules") >> List("module", cast=True, min_length=1)
        bitfield_schema = Schema({
            'caption': Value('@caption'),
            'mask': Value('@mask'),
            'name': Value('@name'),
            'rw': Value('@rw'),
            'values_ref': Value('@values', default=None),
        })

        register_schema = Schema({
            'caption': Value('@caption'),
            'reset': Value('@initval', default=None),
            'name': Value('@name'),
            'offset': Value('@offset'),
            'rw': Value('@rw'),
            'size': Value('@size'),
            'bitfields': List('bitfield', default=None, cast=True, min_length=1) >> bitfield_schema
        })

        register_group_schema = Schema({
            'caption': Value('@caption'),
            'name': Value('@name'),
            'size': Value('@size'),
            'registers': List('register', cast=True, min_length=1) >> register_schema
        })

        module_schema = Schema({
            'caption': Value('@caption'),
            'id': Value('@id'),
            'name': Value('@name'),
            'register_groups': List('register-group', cast=True, min_length=1, default=None, filter=lambda x: not x.get('@class')) >> register_group_schema
        })

        # Variant paths
        variants = root >> Value('variants') >> List('variant', cast=True, min_length=1) >> Schema({
            "order_code": Value('@ordercode'),
            "package": Value('@package'),
            "pinout": Value('@pinout'),
            "speed_max": Value('@speedmax'),
            "temp_max": Value('@tempmax'),
            "temp_min": Value('@tempmin'),
            "vcc_max": Value('@vccmax'),
            "vcc_min": Value('@vccmin'),
        })

        schema = {
            'variants': variants,
            'pinouts': pinouts >> pinout_schema,
            'devices': devices >> device_schema,
            'modules': modules >> module_schema,
        }
        return magic_map(schema, atdf_json)

    def atdf_module(self, module_name):
        for module in self.output['modules']:
            if module['name'] == module_name:
                return module
        raise RuntimeError(f'Module {module_name} not found from atdf')
    """
    def atdf_pinout(self):
        atdf_pinouts = self.atdf_json['avr-tools-device-file']['pinouts']['pinout']
        if not isinstance(atdf_pinouts, list):
            atdf_pinouts = [atdf_pinouts]

        pinouts = []
        for atdf_pinout in atdf_pinouts:
            pins = [{'pad': pin['@pad'], 'pos': pin['@position']} for pin in atdf_pinout['pin']]
            pinout = {
                'name': atdf_pinout['@name'],
                'pins': pins
            }
            pinouts.append(pinout)
        return pinouts
    """

    @staticmethod
    def match_signature(candidate, signature):
        if len(signature) > len(candidate):
            return False
        for signature_col, candidate_col in zip(signature, candidate):
            if signature_col == '*':
                continue
            elif signature_col == '**':
                break
            elif not re.match(signature_col, candidate_col):
                return False

        return True

    def is_valid_table_row(self, index):
        return True

    def read_table(self, header_index):
        header_row = self.datasheet_json[header_index]

        for table_signature in self.table_signatures:
            if self.match_signature(header_row['cols'], table_signature):
                table = [header_row['cols']]
                column_count = len(header_row['cols'])
                row_count = 0
                while True:
                    row_index = header_index + row_count + 1
                    row_columns = self.datasheet_json[row_index]['cols']
                    # TODO check row_i vs row_t
                    # TODO check bitfield
                    # TODO check section?
                    if len(row_columns) == column_count and self.is_valid_table_row(row_index):
                        table.append(row_columns)
                        row_count += 1
                    else:
                        break
                if row_count == 0:
                    return False
                return table
        return False

    def match_signature_definition(self, index, signature_definition):
        for offset, signature_row in enumerate(signature_definition):
            cols = self.datasheet_json[index+offset]['cols']
            if not self.match_signature(cols, signature_row):
                return False
        return True


    def process(self):
        raise NotImplemented

