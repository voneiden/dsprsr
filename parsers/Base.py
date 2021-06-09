import re


class BaseParser:
    table_signatures = []
    module_signature = []

    def __init__(self, atdf_json, datasheet_json):
        self.atdf_json = atdf_json
        self.datasheet_json = datasheet_json

    def atdf_modules(self):
        return

    def atdf_module(self, module_name):
        for module in self.atdf_json['avr-tools-device-file']['modules']['module']:
            if module['@name'] == module_name:
                return module
        raise RuntimeError(f'Module {module_name} not found from atdf')

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

    def read_table(self, header_index):
        header_row = self.datasheet_json[header_index]

        for table_signature in self.table_signatures:
            if self.match_signature(header_row['cols'], table_signature):
                table = [header_row['cols']]
                column_count = len(header_row['cols'])
                row_count = 0
                while True:
                    row_columns = self.datasheet_json[header_index + row_count + 1]['cols']
                    if len(row_columns) == column_count:
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

