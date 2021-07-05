import argparse
import os
import sys
import pandas as pd
from openclio import argsIOrole

parser = argparse.ArgumentParser(
    description='openclio - figuring out the input/output arguments of an OpenCL kernel',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-f', '--file',
    type=str,
    required=True,
    help='the *.cl or *.ll file with the OpenCL kernel(s)'
)

parser.add_argument('-k', '--kernel',
    type=str,
    required=True,
    help='the name of the kernel to examine'
)

parser.add_argument('--tablefmt',
    type=str,
    default='fancy_grid',
    help='tabulate tablefmt argument (default: fancy_grid)'
)

parser.add_argument('--csv',
    action='store_true',
    help='print output as csv (overrides --tablefmt)'
)

def run():

    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(f'file `{args.file}` does not exist')

    with open(args.file, 'r') as f:
        source = f.read()

    iorole, arglist = argsIOrole(args.kernel, source, args.file, arglist=True)

    # pretty print results
    column_labels = ['Name', 'Type', 'Input', 'Output']
    iorole_for_df = []
    for argnametype in arglist:
        argname = argnametype.strip().split('%')[1]
        argtype = argnametype.strip().split(' %')[0]
        argiorole = ['', '']
        if 'input' in iorole[argnametype]:
            argiorole[0] = 'X'
        if 'output' in iorole[argnametype]:
            argiorole[1] = 'X'
        iorole_for_df.append([argname, argtype, *argiorole])

    df = pd.DataFrame(iorole_for_df, columns=column_labels)
    df.index += 1
    df.index.name = 'Position'

    if args.csv:
        df.replace('X', 1, inplace=True)
        df.replace('', 0, inplace=True)
        output = df.to_csv()
    else:
        from tabulate import tabulate
        output = tabulate(
            df,
            headers='keys',
            tablefmt=args.tablefmt,
            stralign='center'
        )

    sys.stderr.write(f'I/O role of the arguments of OpenCL kernel {args.file}:{args.kernel}\n')
    print(output)
