def parse_csv_file(filename, has_header_row):
    csv_file = open(filename, 'r')
    csv_lines = csv_file.readlines()
    if has_header_row:
        del csv_lines[0]

    csv_file.close()

    return parse_csv(csv_lines)


def parse_csv(csv_lines):
    rows = []
    for line in csv_lines:
        row = parse_line(line)
        rows.append(row)
    
    return rows

def parse_line(line):
    new = 0
    string = 1
    qstring = 2
    quote = 3
    minus = 4
    point = 5
    number = 6
    fnumber = 7

    ps = new  # parse state
    fields = []
    value = ''

    if line.endswith('\n'):
        line = line[:-1]

    for index, char in enumerate(line):
        if (ps == new):
            if (char == ','):
                fields.append(None)
            elif (char == '"'):
                ps = qstring
                value = ''
            elif (char == '.'):
                ps = point
                value = char
            elif (char == '-'):
                ps = minus
                value = char
            elif (char.isdigit()):
                ps = number
                value = char
            else:
                ps = string
                value = char
        elif (ps == string):
            if (char == ','):
                fields.append(value)
                ps = new
            else:
                value = value + char
        elif (ps == qstring):
            if (char == '"'):
                ps = quote
            else:
                value = value + char
        elif (ps == quote):
            if (char == ','):
                fields.append(value)
                ps = new
            elif (char == '"'):
                value = value + '"'
                ps = qstring
            else:
                raise Exception('end of string expected after quote')
        elif (ps == minus):
            if (char == ','):
                # interpret as a string
                fields.append(value)
                ps = new
            elif (char == '.'):
                value = value + char
                ps = point
            elif (char.isdigit()):
                value = value + char
                ps = number
            else:
                # interpret as a string
                value += char
                ps = string
        elif (ps == point):
            if (char == ','):
                # interpret as a string
                fields.append(value)
                ps = new
            elif (char.isdigit()):
                value += char
                ps = fnumber
            else:
                # interpret as a string
                value += char
                ps = string
        elif (ps == number):
            if (char == ','):
                fields.append(int(value))
                ps = new
            elif (char == '.'):
                value = value + '.'
                ps = fnumber
            elif (not char.isdigit()):
                value = value + char
                ps = string
            else:
                value = value + char
        elif (ps == fnumber):
            if (char == ','):
                fields.append(float(value))
                ps = new
            elif (not char.isdigit()):
                value = value + char
                ps = string
            else:
                value = value + char

    # end of line, process final field
    if (ps == new):
        fields.append(None)
    elif (ps == string):
        fields.append(value)
    elif (ps == qstring):
        raise Exception('missing closing quote')
    elif (ps == quote):
        fields.append(value)
    elif (ps == minus):
        # interpret as a string
        fields.append(value)
    elif (ps == number):
        fields.append(int(value))
    elif (ps == fnumber):
        fields.append(float(value))
        
    return fields

def encode_string(value):
    if '\n' in value:
        raise Exception('strings must not contain <newline> character ("\n")')

    if (',' not in value) and ('"' not in value):
        return value
    
    return '"' + value.replace('"', '""') + '"'

def line(fields):
    record = ''
    for value in fields:
        if isinstance(value, str):
            record += encode_string(value)
        elif value is not None:
            record += str(value)
        record += ','

    return record[:-1] + '\n'


def write_csv_file(header, records, filename):
    lines = []
    lines.append(header)
    for record in records:
        lines.append(line(record.fields()))
    
    # strip newline off the last line
    lines[-1] = lines[-1][:-1]

    csv_file = open(filename, 'w')
    csv_file.writelines(lines)
    csv_file.close()
