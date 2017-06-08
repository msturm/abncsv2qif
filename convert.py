#!/usr/bin/env python
import csv
import argparse
import datetime
import re
import sys


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
    elif desc.startswith("/TRTP") or desc.startswith("SEPA"):
        result = parse_sepa(desc)
    else:
        result['name'] = desc[0:33].split(",")[0].strip()
        result['description'] = desc[33:].strip() if len(desc) >= 33 else ''
    return result


def parse_sepa(desc):
    desc = remove_65_char_space(desc)
    result = {}

    if desc is None:
        print "Error while parsing file"
        return None
#    print "curline: " + desc
    if desc.startswith("/TRTP/SEPA OVERBOEKING") \
            or desc.startswith("/TRTP/SEPA Incasso algemeen doorlopend") \
            or desc.startswith("/TRTP/iDEAL") \
            or desc.startswith("/TRTP/Acceptgirobetaling"):
        result['name'] = re.findall(" ?/NAME/ ?(.*?)/", desc)[0]
        if desc.startswith("/TRTP/SEPA Incasso algemeen doorlopend"):
            description_regex_result = re.findall("/REMI/(.*?)/IBAN", desc)
        else:
            description_regex_result = re.findall("/REMI/(.*?)/", desc)

        if len(description_regex_result) > 0:
            result['description'] = description_regex_result[0]
        else:
            result['description'] = ""
    elif desc.startswith("SEPA Overboeking") or desc.startswith("SEPA Periodieke overb."):
        if "Omschrijving:" in desc:
            result['name'] = re.findall(".*Naam: (.*) Omschrijving:", desc)[0].strip()
            result['description'] = remove_33_char_space(re.findall(".*(Omschrijving: .*)", desc)[0])[14:].strip()
        else:
            result['name'] = re.findall(".*Naam: (.*)", desc)[0].strip()
            result['description'] = ''
    elif desc.startswith("SEPA Incasso algemeen doorlopend"):
        result['name'] = re.findall("Naam: (.*) Machtiging:", desc)[0].strip()
        if "IBAN:" in desc:
            result['description'] = re.findall("Omschrijving: (.*)IBAN:", desc)[0].strip()
        else:
            result['description'] = re.findall("Omschrijving: (.*)", desc)[0].strip()
    else:
        print "Error while parsing " + desc
        result['name'] = ''
        result['description'] = ''
    return result


def remove_33_char_space(desc):
    if len(desc) < 33:
        return desc
    elif desc[32] == ' ':
        return desc[0:32] + remove_33_char_space(desc[33:])
    else:
        return desc


def remove_65_char_space(desc):
    if len(desc) < 66:
        return desc
    elif desc[65] == ' ':
        return desc[0:65] + remove_65_char_space(desc[66:])
    elif desc[64] == ' ':
        return desc[0:64] + remove_65_char_space(desc[65:])
    elif desc[63] == ' ':
        return desc[0:63] + remove_65_char_space(desc[64:])
    else:
        return desc


def print_qif_header():
    return "!Type:Bank\n"


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
        if desc_line_result is None:
            print "error in line {}".format(row)
            sys.exit()
        result.append({'date': row[2], 'amount': row[6], 'description': desc_line_result['description'], 'name': desc_line_result['name']})
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert csv to qif')
    parser.add_argument("filename", help='csv filename to convert')
    args = parser.parse_args()

    totalresult = ""
    with open(args.filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        totalresult = print_qif_header()
        counter = 1
        for row in parse_file(csvreader):
            #print "processing line: " + str(counter)
            counter += 1
            totalresult += print_qif_stmt(row)

    print totalresult
