
import argparse
import sys
import re


def output(line):
    print(line)


def grep(lines, params):
    #after_context=0, before_context=0, context=0, count=False, ignore_case=True, invert=False, line_number=False, pattern='e'
    print(str(params.pattern))

    trans_table={ord('*'): '.*', 
    ord('?'): '.?', 
    ord('.'): '\.', 
    ord('^'): '\^', 
    ord('\\'): r'\\', 
    ord('$'): '\$', 
    ord('+'): '\+',
    ord('('): '\(', 
    ord('{'): '\[', 
    ord('['): '\{', 
    ord('|'): '\|', } #translation table


    re_pattern=params.pattern.translate(trans_table) # translating grep pattern to python regex pattern
    print(re_pattern)
    pattern=re.compile(re_pattern, re.I)
    
    for line in lines:
        line = line.rstrip()
        if re.search(pattern, line):
            output(line)


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()