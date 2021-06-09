def _convert_row(row, col_widths):
    cols = []
    last_col_ci = len(col_widths) - 1
    for ci, col in enumerate(row):
        fixed = f'{col:<{col_widths[ci]}}'
        cols.append(f'| {fixed} ')
        if ci == last_col_ci:
            cols.append(f'|')
    return ''.join(cols)

def markdown_table(table):
    row_count = len(table)
    col_count = len(table[0])

    col_widths = [5 for _ in range(col_count)]

    for row in table:
        for ci, col in enumerate(row):
            col_widths[ci] = max(col_widths[ci], len(col))

    header = table[0]
    rows = table[1:]

    output = ['\n']

    cols = []

    output.append(_convert_row(header, col_widths))
    output.append(_convert_row([f':{"-"*(ci-1)}' for ci in col_widths], col_widths))
    for row in rows:
        output.append(_convert_row(row, col_widths))

    output.append('\n')
    output = '\n'.join(output)
    return output
