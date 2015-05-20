#!/usr/bin/env python
import csv
import argparse
import datetime
import re


def fix_date(rawdate):
    return datetime.datetime.strptime(rawdate, "%Y%m%d").strftime("%d/%m/%Y")


def parse_description(desc):
    result = {}
    if desc.startswith("BEA"):
        result['name'] = desc[33:66].split(",")[0]
        result['description'] = desc[99:166] if len(desc) > 99 else ''
    elif desc.startswith("GEA"):
        result['name'] = "Geldautomaat " + desc[33:66].split(",")[0]
        result['description'] = ''
    elif desc.startswith("/TRTP"):
        result = parse_sepa(desc)
    else:
        result['name'] = desc[0:33].split(",")[0].strip()
        result['description'] = desc[33:] if len(desc) >= 33 else ''
    return result


def parse_sepa(desc):
    desc = remove_65_char_space(desc)
    result = {}
    if desc.startswith("/TRTP/SEPA OVERBOEKING") \
            or desc.startswith("/TRTP/SEPA Incasso algemeen doorlopend") \
            or desc.startswith("/TRTP/iDEAL"):
        result['name'] = re.findall(" ?/NAME/ ?(.*?)/", desc)[0]
        if desc.startswith("/TRTP/SEPA Incasso algemeen doorlopend"):
            description_regex = re.findall("/REMI/(.*?)/IBAN", desc)
        else:
            description_regex = re.findall("/REMI/(.*?)/", desc)

        if len(description_regex) > 0:
            result['description'] = description_regex[0]
        else:
            result['description'] = ""
    else:
        print "Error while parsing " + desc
        result['name'] = ''
        result['description'] = ''
    return result


def remove_65_char_space(desc):
    if len(desc) < 66:
        return desc
    elif desc[65] == ' ':
        return desc[0:65] + remove_65_char_space(desc[66:])
    elif desc[64] == ' ':
        return desc[0:64] + remove_65_char_space(desc[65:])
    elif desc[63] == ' ':
        return desc[0:63] + remove_65_char_space(desc[64:])


def format_name(desc):
    name = ""
    if desc.startswith("BEA"):
        name = desc[33:66].split(",")[0]
    elif desc.startswith("GEA"):
        name = "Geldautomaat " + desc[33:66]
        number = 'TRANSFER'
    elif desc.startswith("CHIP"):
        name = "Chipknip " + desc[33:66]
        number = 'TRANSFER'
    elif desc.startswith("GIRO"):
        if desc.startswith("GIRO    "):
            name = desc.replace('    ', '  ', 1)[14:31]
        else:
            name = desc[14:33]

        if name.strip() == "":
            name = desc[33:66].strip()
    elif desc.startswith("/TRTP/SEPA"):
        if '/REMI/' in desc:
            name = desc[desc.index('/NAME/') + 6:desc.index('/REMI/')]
        else:
            name = desc[desc.index('/NAME/') + 6:desc.index('/EREF/')]
    else:
        name = desc[14:33]
        if name.strip() == "":
            name = desc[33:66]
    return name;


def print_qif_header():
    return "!Type:Bank"


def print_qif_stmt(data):
    number = ""
    name = data['name']
    memo = data['description']
    date = data['date']
    amount = data['amount']
    result = ""
    result += "D{}\n".format(fix_date(date))
    result += "T{}\n".format(amount).replace(",", ".")
    result += "P{}\n".format(name)
    if memo.strip() != "":
        result += "M{}\n".format(memo)
    if number.strip() != "":
        result += "N{}\n".format(number)
    result += "^\n"
    return result


def parse_file(csvreader):
    result = []
    for row in csvreader:
        desc_line_result = parse_description(row[7])
        result.append({'date': row[2], 'amount': row[6], 'description': desc_line_result['description'], 'name': desc_line_result['name']})
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert csv to ofx')
    parser.add_argument("filename", help='csv filename to convert')
    args = parser.parse_args()

    result = ""
    with open(args.filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        result = print_qif_header()
        counter = 1
        for row in parse_file(csvreader):
            #print "processing line: " + str(counter)
            counter += 1
            result += print_qif_stmt(row)

    print result
