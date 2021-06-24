import re

from parsers.Base import BaseParser
from parsers.extra.tiny_1series_updi_interface import UPDI_INTERFACE
from utils.markdown_table import markdown_table

re_section_raw = r'^\d+\.(\d+\.)*'
re_section = re.compile(re_section_raw)
re_register_name_wildcard = (re.compile(r'([A-Za-z_]+)(\d|10)($|[A-Za-z_]+)'), r'\1[\2nx]\3')

class ATtiny814Parser(BaseParser):
    table_signatures = [
        ('Value', '**'),
        ('ASYNCUSERn', 'User Multiplexer', 'Description')
    ]
    module_signature = ((re_section, re.compile('Register Summary(?:$|[^.])')),)
    module_name_map = {'Memories': 'FUSE', 'AVR®': 'CPU', 'Peripherals': 'SYSCFG'}
    module_name_hint_map = {
        'ADC.ADCn': ('ADC', 'ADC'),
        'PORT.PORTx': ('PORT', 'PORT'),
        'PORT.VPORTx': ('VPORT', 'VPORT'),
        'TCA.Normal Mode': ('TCA', 'TCA_SINGLE'),
        'TCA.Split Mode': ('TCA', 'TCA_SPLIT'),
    }

    register_name_map = {
        'SPL': 'SP',
        'SPH': 'SP',
    }

    register_signature = (('Name:', '*'), ('Offset:', '*'))
    bitfield_signature = ((re.compile(r'Bit.*-.*'), '**'),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output['modules'].append(UPDI_INTERFACE)

    def is_valid_table_row(self, index):
        return not self.match_signature_definition(index, self.bitfield_signature)

    def scan_field_description(self, index):
        description = []
        section_signature = ((re_section,),)

        while not self.match_signature_definition(index, section_signature) and not self.match_signature_definition(index, self.bitfield_signature):
            # TODO end of page
            row = self.datasheet_json[index]
            table = self.read_table(index)
            if table:
                description.append(markdown_table(table))
                index += len(table) - 1
                row = self.datasheet_json[index]
            else:
                description.append(" ".join(row['cols']))

            if row['_metadata']['row_i'] < row['_metadata']['row_t'] - 4:
                index += 1
            else:
                index += 4
        #print("D)", self.datasheet_json[index])
        #print("M1)", self.match_signature_definition(index, section_signature))
        #print("M2)", self.match_signature_definition(index, bitfield_signature))
        description = "\n".join(description)
        print("---->", description)
        return description

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
        field_description = self.scan_field_description(index+1)
        return field_description

    def scan_register(self, index, register_name, atdf_bitfields):
        fields = []
        if register_name in self.register_name_map:
            register_name = self.register_name_map[register_name]
        re_register_name = re.compile(re.sub(*re_register_name_wildcard, register_name))
        register_signature = (('Name:', re_register_name), ('Offset:', '*'))

        try:
            while not self.match_signature_definition(index, register_signature):
                index += 1
        except IndexError:
            print("WHOA, undocumented feature!", register_name)
            #TODO
            return fields
        print(f"* Found register {register_name} at index", index)
        for atdf_bitfield in atdf_bitfields:
            print("ATDFBITFIELD", atdf_bitfield, "err", atdf_bitfields)
            atdf_bitfield['description'] = self.scan_field(index, atdf_bitfield['name'], atdf_bitfield['mask'])

    def process(self):
        skip = 0
        modules = []
        for index, row in enumerate(self.datasheet_json):
            if skip > 0:
                skip -= 1
                continue
            if self.match_signature_definition(index, self.module_signature):
                # Determine module - now this is a hack :-D
                page_header_offset = row['_metadata']['row_t'] - row['_metadata']['row_i'] - 2
                page_title = self.datasheet_json[index + page_header_offset]['cols'][0]
                module_name = page_title.split(' ')[0]
                if module_name in self.module_name_map:
                    module_name = self.module_name_map[module_name]

                # Sometimes we can't rely on the page header title
                register_group_name = None
                module_name_hint = row['cols'][1]
                if ' - ' in module_name_hint:
                    module_name_hint = module_name_hint.split(' - ')[1]
                    if module_name_hint != module_name:
                        module_name_hint_key = f'{module_name}.{module_name_hint}'
                        module_name, register_group_name = self.module_name_hint_map.get(module_name_hint_key) or (None, None)
                        if not module_name:
                            raise RuntimeError(f'Module name hint key yielded no results: {module_name_hint_key}')

                atdf_module = self.atdf_module(module_name)
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
                    print(atdf_register, atdf_registers)
                    register_name = atdf_register['name']

                    # TODO add register extra description?

                    #print(atdf_register)
                    atdf_bitfields = atdf_register.get('bitfields')
                    if atdf_bitfields:
                        self.scan_register(index + 1, register_name, atdf_bitfields)
