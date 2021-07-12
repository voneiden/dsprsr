import re
from typing import Callable

from parsers.Base import BaseParser
from parsers.extra.tiny_1series_updi_interface import UPDI_INTERFACE
from utils.markdown_table import markdown_table

re_section_raw = r'^\d+((\.\d+)+|\.)'
re_section = re.compile(re_section_raw)
re_register_name_wildcard = (re.compile(r'([A-Za-z_]+)(\d|10)($|[A-Za-z_]+)'), r'\1[\2nx]\3')

class ATtiny814Parser(BaseParser):
    table_signatures = [
        ('Value', '**'),
        ('ASYNCUSERn', 'User Multiplexer', 'Description')
    ]
    module_signature = ((re_section, re.compile('Register Summary.*')),)

    # RTC is a black sheep
    module_signature_alt = ((re.compile(re_section_raw + r'\s+Register Summary.*'),),)

    module_name_map = {'Memories': 'FUSE', 'AVR®': 'CPU', 'Peripherals': 'SYSCFG'}
    module_name_hint_map = {
        'ADC.ADCn': ('ADC', 'ADC'),
        'PORT.PORTx': ('PORT', 'PORT'),
        'PORT.VPORTx': ('VPORT', 'VPORT'),
        'TCA.Normal Mode': ('TCA', 'TCA_SINGLE'),
        'TCA.Split Mode': ('TCA', 'TCA_SPLIT'),
        'FUSE.GPIOR': ('FUSE', 'GPIO'),  # ATTiny202
        'AVR.CPU': ('CPU', 'CPU'),  # ATTiny202
        'Nonvolatile.NVMCTRL': ('NVMCTRL', 'NVMCTRL'),  # ATTiny202<
        'Clock.CLKCTRL': ('CLKCTRL', 'CLKCTRL'),  # ATTiny202
        'Sleep.SLPCTRL': ('SLPCTRL', 'SLPCTRL'),  # ATTiny202
        'Reset.RSTCTRL': ('RSTCTRL', 'RSTCTRL'),  # ATTiny202
        'CPU.CPUINT': ('CPUINT', 'CPUINT'),  # ATTiny202
        'Event.EVSYS': ('EVSYS', 'EVSYS'),  # ATTiny202
        'Port.PORTMUX': ('PORTMUX', 'PORTMUX'),  # ATTiny202
        'I/O.PORT': ('PORT', 'PORT'),  # ATTiny202
        'I/O.VPORT': ('VPORT', 'VPORT'),  # ATTiny202
        'Brown-Out.BOD': ('BOD', 'BOD'),  # ATTiny202
    }

    register_name_map = {
        'SPL': 'SP',
        'SPH': 'SP',
    }

    register_signature = (('Name:', '*'), ('Offset:', '*'))
    property_signature = (('Property:', '*'),)
    bitfield_signature = ((re.compile(r'Bit.*-.*'), '**'),)
    bittable_signature = (('Bit', '**'),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output['modules'].append(UPDI_INTERFACE)

    def is_valid_table_row(self, index):
        return not self.match_signature_definition(index, self.bitfield_signature)

    def scan_text(self, index, end_condition: Callable, start_condition: Callable = None, start_after_condition=False):
        text = []
        if start_condition:
            try:
                while not start_condition(index):
                    index += 1
            except IndexError:
                print("! Failed to read text (start EOF)")
                return []
            if start_after_condition:
                index += 1

        try:
            while not end_condition(index):
                row = self.datasheet_json[index]
                rows_left = row['_metadata']['row_t'] - row['_metadata']['row_i']

                if rows_left < 4:
                    index += rows_left
                    print("Skipping straight to next page")
                    continue

                table = self.read_table(index)
                if table:
                    text.append(markdown_table(table))
                    index += len(table) - 1
                    row = self.datasheet_json[index]
                else:
                    text.append(" ".join(row['cols']))

                # TODO support for variable page end lengths
                rows_left = row['_metadata']['row_t'] - row['_metadata']['row_i']
                if rows_left < 5:
                    index += rows_left
                else:
                    index += 1
        except IndexError:
            print("! Failed to read text (end EOF)")
            return []
        return "\n".join(text)

    def field_description_end_condition(self, index):
        section_signature = ((re_section,),)
        return self.match_signature_definition(index, section_signature) or self.match_signature_definition(index, self.bitfield_signature)

    def scan_field_description(self, index):
        return self.scan_text(index, self.field_description_end_condition)

    def registry_description_start_condition(self, index):
        return self.match_signature_definition(index, self.property_signature)

    def registry_description_end_condition(self, index):
        return self.match_signature_definition(index, self.bittable_signature)

    def scan_registry_description(self, index):
        return self.scan_text(index,
                              self.registry_description_end_condition,
                              start_condition=self.registry_description_start_condition,
                              start_after_condition=True
                              )

    def scan_field(self, index, field_name, field_mask):
        field_description = None
        # TODO signature via bitmask?
        # Bits 0:3, 4:7 -->
        print("Field mask", field_mask)
        field_mask = bin(int(field_mask, 16))[2:][::-1]
        field_low_bit = field_mask.index('1')
        field_high_bit = field_mask.rindex('1')
        if field_low_bit == field_high_bit:
            re_bit = field_low_bit
        else:
            # Enterprise level consistency in the datasheet endianness
            re_bit = f'({field_low_bit}:{field_high_bit}|{field_high_bit}:{field_low_bit})'

        # What could go wrong?
        bitfield_signature = ((re.compile(f'Bit.*{re_bit}.*-.*'), '**'),)

        try:
            while not self.match_signature_definition(index, bitfield_signature):
                index += 1
        except IndexError:
            print("!!! WHOA, undocumented BITFIELD!", field_name, "using re_bit", re_bit)
            return None

        print(f" - Found bitfield {field_name} at index {index}")
        caption = self.datasheet_json[index]['cols'][1]
        field_description = self.scan_field_description(index+1)
        return caption, field_description

    def scan_register(self, index, atdf_register):
        register_name = atdf_register['name']
        atdf_bitfields = atdf_register.get('bitfields')

        if register_name in self.register_name_map:
            register_name = self.register_name_map[register_name]
        re_register_name = re.compile(re.sub(*re_register_name_wildcard, register_name))
        register_signature = (('Name:', re_register_name), ('Offset:', '*'))

        try:
            while not self.match_signature_definition(index, register_signature):
                index += 1
        except IndexError:
            print("WHOA, undocumented feature!", register_name)  # TODO
            atdf_register['description'] = 'Undocumented'
            return

        print(f"* Found register {register_name} at index", index)
        atdf_register['description'] = self.scan_registry_description(index) or None
        # ATDF is missing sometimes bitfields for fields that have only one field? Guess from the size
        if not atdf_bitfields and atdf_register['size'] >= 1:
            # Manually generate bitfields with best guess :E
            atdf_bitfields = [
                {
                    'name': register_name,
                    'caption': None,
                    'mask': hex(0xff << (8*i)),
                    'rw': 'unknown',  # TODO ? This can in theory be parsed
                    'values_ref': None

                } for i in range(atdf_register['size'])
            ]
            atdf_register['bitfields'] = atdf_bitfields

        if atdf_bitfields:
            for atdf_bitfield in atdf_bitfields:
                caption, description = self.scan_field(index, atdf_bitfield['name'], atdf_bitfield['mask'])
                atdf_bitfield['description'] = description
                if not atdf_bitfield['caption']:
                    atdf_bitfield['caption'] = caption

    def atdf_modules(self, module_name):
        if module_name == "FUSE":  # AKA Memories
            return [self.atdf_module("GPIO"),
                    self.atdf_module("FUSE"),
                    self.atdf_module("LOCKBIT"),
                    self.atdf_module("SIGROW"),
                    self.atdf_module("USERROW"),  # Userrow is not described as a register in the DS
                    ]
        return [self.atdf_module(module_name)]

    def process(self):
        skip = 0
        start_page = 12

        for index, row in enumerate(self.datasheet_json):
            if skip > 0:
                skip -= 1
                continue
            if row['_metadata']['page'] < start_page:
                continue
            if self.match_signature_definition(index, self.module_signature) or \
                    self.match_signature_definition(index, self.module_signature_alt):
                print("MATCH ROW", row)
                # Determine module - now this is a hack :-D
                page_header_offset = row['_metadata']['row_t'] - row['_metadata']['row_i'] - 2
                page_title = self.datasheet_json[index + page_header_offset]['cols'][0]
                module_name = page_title.split(' ')[0]
                if module_name in self.module_name_map:
                    module_name = self.module_name_map[module_name]
                # Sometimes we can't rely on the page header title
                register_group_name = None
                module_name_hint = row['cols'][1] if len(row['cols']) > 1 else None
                if module_name_hint and ' - ' in module_name_hint:
                    module_name_hint = module_name_hint.split(' - ')[1]
                    if module_name_hint != module_name:
                        module_name_hint_key = f'{module_name}.{module_name_hint}'
                        module_name, register_group_name = self.module_name_hint_map.get(module_name_hint_key) or (None, None)
                        if not module_name:
                            raise RuntimeError(f'Module name hint key yielded no results: {module_name_hint_key}')

                # Datasheet section "Memories" is tricky, it contains registries from multiple modules
                atdf_modules = self.atdf_modules(module_name)
                for atdf_module in atdf_modules:
                    register_groups = atdf_module['register_groups']
                    if len(register_groups) > 1:
                        if register_group_name is None:
                            raise RuntimeError(f'register_group_name was not defined for module {module_name} but register_group contains multiple entries')
                        register_group = next(rg for rg in register_groups if rg['name'] == register_group_name)
                    else:
                        register_group = register_groups[0]
                    module_name = register_group['name']
                    print(f"Found module: {module_name} (page {row['_metadata']['page']})")

                    atdf_registers = register_group['registers']
                    for atdf_register in atdf_registers:
                        self.scan_register(index + 1, atdf_register)
