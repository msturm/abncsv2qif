#!/usr/bin/env python
import csv
import argparse
import datetime

parser = argparse.ArgumentParser(description='Convert csv to ofx')
parser.add_argument("filename", help='csv filename to convert')
args = parser.parse_args()


def print_qif_header():
    print "!Type:Bank"

def fix_date(rawdate):
    return datetime.datetime.strptime(rawdate, "%Y%m%d").strftime("%d/%m/%Y")

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

def print_qif_stmt(date, amount, desc, memo=None):
    number = ""
    name = format_name(desc)
    if memo == None:
        memo = desc[99:166]
    print "D{}".format(fix_date(date))
    print "T{}".format(amount).replace(",", ".")
    print "P{}".format(name)
    if memo.strip() != "":
        print "M{}".format(memo)
    if number.strip() != "":
        print "N{}".format(number)
    print "^"

with open(args.filename, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter="\t")
    print_qif_header()
    counter = 1
    for row in csvreader:
        #print "processing line: " + str(counter)
        counter += 1
        print_qif_stmt(row[2], row[6], row[7]) 
