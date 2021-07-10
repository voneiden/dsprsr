import re
from typing import Callable

from parsers.ATtiny814 import ATtiny814Parser
from parsers.extra.tiny_1series_updi_interface import UPDI_INTERFACE
from utils.markdown_table import markdown_table

re_section_raw = r'^\d+((\.\d+)+|\.)'
re_section = re.compile(re_section_raw)
re_register_name_wildcard = (re.compile(r'([A-Za-z_]+)(\d|10)($|[A-Za-z_]+)'), r'\1[\2nx]\3')

class ATtiny202Parser(ATtiny814Parser):

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

    module_name_map = {
        'GPIOR': ('GPIO', 'GPIO'),
        'ADCn': ('ADC', 'ADC'),
        'TCA in Normal Mode (CTRLD.SPLITM=0)': ('TCA', 'TCA_SINGLE'),
        'TCA in Split Mode (CTRLD.SPLITM=1)': ('TCA', 'TCA_SPLIT')
    }

    module_signature = ((re_section, re.compile('(Register|Fuse) Summary.*')),)

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
        # TODO TCA.SPLIT in register summary causes the signature to not match (becaues dot not allowed!)
        skip = 0
        start_page = 9
        modules = []
        for index, row in enumerate(self.datasheet_json):
            if skip > 0:
                skip -= 1
                continue
            if row['_metadata']['page'] < start_page:
                continue
            if self.match_signature_definition(index, self.module_signature) or \
                    self.match_signature_definition(index, self.module_signature_alt):
                print("MATCH ROW", row)
                summary_tokens = " ".join(row['cols']).split(' - ')
                module_name = summary_tokens[1]
                register_group_name = module_name # TODO

                if module_name in self.module_name_map:
                    module_name, register_group_name = self.module_name_map[module_name]


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
