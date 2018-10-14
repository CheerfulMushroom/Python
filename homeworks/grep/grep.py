
import argparse
import sys
import re


def output(queue, need_line_number,  is_searched):      
    output.last_index = getattr(output, 'last_index', queue[0][0])
    if queue[0][0] - output.last_index > 1:
        print('--')

    for index, line in queue:
        if is_searched:
            print(f'{index}:{line}' if need_line_number else line)
        else:
            print(f'{index}-{line}' if need_line_number else line)
        output.last_index = index

def grep(lines, params):
    #after_context=0, before_context=0, context=0, count=False, ignore_case=True, invert=False, line_number=False, pattern='e'

    # translating grep pattern to python regex pattern
    re_pattern=re.escape(params.pattern)
    re_pattern=re_pattern.replace(r'\?', '.?').replace(r'\*', '.*') 
    if params.ignore_case:
        pattern=re.compile(re_pattern, re.I)
    else:
        pattern=re.compile(re_pattern)
   
    before = list()
    after = list()
    amount_of_lines_after = params.after_context or params.context
    amount_of_lines_before = params.before_context or params.context
    after_found_line = False

    for index, line in enumerate(lines):
        line = line.rstrip()
        if re.search(pattern, line):
            if before:
                output(before, params.line_number,  is_searched = False)
            output([(index, line)], params.line_number,  is_searched = True)
            before.clear()
            after_found_line = True
        else:
            if not after_found_line:
                before.append((index, line))
                if len(before) > amount_of_lines_before:
                    before.pop(0)
            else: 
                after.append((index, line))
                if len(after) == amount_of_lines_after:
                    if after:
                        output(after, params.line_number,  is_searched = False)
                    after.clear()
                    after_found_line = False



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
    import random
    lines = [str('line {}'.format(random.randint(1,10))) for i in range(20) ]
    print('\n'.join(line for line in lines))
    print('')
    params = parse_args(sys.argv[1:])
    grep(lines, params)
    # grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()