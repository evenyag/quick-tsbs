#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import subprocess

# Current working directory
CWD = os.getcwd()
DEFAULT_WORKSPACE = '%s/workspace' % CWD

def generate(args):
    print(args)
    pass

def greptime(args):
    print(args)
    pass

if __name__ == '__main__':
    # Instantiate the parser
    parser = argparse.ArgumentParser(prog='QuickTSBS', description='Quick TSBS Setup')
    parser.add_argument('--workspace', default=DEFAULT_WORKSPACE, help='workspace directory')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Parser for the "generate" command
    generate_parser = subparsers.add_parser('generate', help='generate help')
    generate_parser.add_argument('-o', '--output', help='output file path')
    generate_parser.set_defaults(func=generate)

    # Parser for the "greptime" command
    greptime_parser = subparsers.add_parser('greptime', help='greptime help')
    greptime_parser.set_defaults(func=greptime)

    if len(sys.argv) == 1:
        parser.print_help()
        # parser.print_usage() # for just the usage line
        parser.exit()

    # Parse arguments
    args = parser.parse_args()
    args.func(args)
