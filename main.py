#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import subprocess
import yaml

from pathlib import Path

# Current working directory
CWD = os.getcwd()
DEFAULT_WORKSPACE = '%s/workspace' % CWD
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
TSBS_SRC_DIR = '%s/tsbs' % PROJECT_DIR
SCRIPT_DIR = '%s/scripts' % PROJECT_DIR
CONFIG_DIR = '%s/config' % PROJECT_DIR
# Default bench data file name.
BENCH_DATA_FILE = 'bench-data.lp'

class WorkspacePaths(object):
    def __init__(self, workspace):
        self.workspace = workspace
        self.binary_dir = '%s/bin' % workspace
        self.tsbs_binary_dir = '%s/tsbs' % self.binary_dir
        self.data_generator_path = '%s/tsbs_generate_data' % self.tsbs_binary_dir
        self.tsbs_load_greptime = '%s/tsbs_load_greptime.yaml' % workspace

class BenchConfig(object):
    def __init__(self, input_file):
        self.file = input_file
        self.urls = 'http://localhost:4000'
        self.gzip = False
        self.batch_size = '100'
        self.workers = 4

    def read_from_config(self, config):
        loader = config['loader']
        self.file = config['data-source']['file']['location']
        self.urls = loader['db-specific']['urls']
        self.gzip = loader['db-specific']['gzip']
        self.batch_size = loader['runner']['batch-size']
        self.workers = loader['runner']['workers']

    def write_to_config(self, config):
        loader = config['loader']
        config['data-source']['file']['location'] = self.file
        loader['db-specific']['urls'] = self.urls
        loader['db-specific']['gzip'] = self.gzip
        loader['runner']['batch-size'] = self.batch_size
        loader['runner']['workers'] = self.workers

def is_file_exists(path):
    file = Path(path)
    return file.exists()

def run_cmd(cmd, name):
    print('Try to run command: %s' % cmd)
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        print('%s start...' % name)
        print('%s output is:' % name)
        for line in proc.stdout:
            print(line.decode('utf-8'), end='')
        errs = proc.communicate()[1]
        if proc.returncode != 0:
            print('%s error is %s' % (name, errs))
        print('%s end...' % name)

def maybe_build_tsbs(paths):
    if is_file_exists(paths.data_generator_path):
        # tsbs generator exists
        print('tsbs exists at workspace')
        return
    # Invokd script to build tsbs and move binaries to tsbs_binary_dir
    cmd = '%s/build_tsbs.sh %s %s' % (SCRIPT_DIR, TSBS_SRC_DIR, paths.tsbs_binary_dir)
    run_cmd(cmd, 'Build tsbs')

def generate_data(data_generator_path, output_file):
    cmd = '%s --use-case="cpu-only" --seed=123 --scale=4000 \
--timestamp-start="2016-01-01T00:00:00Z" \
--timestamp-end="2016-01-01T06:00:00Z" \
--log-interval="10s" --format="influx" > %s' % (data_generator_path, output_file)
    run_cmd(cmd, 'Generate data')

def load_yaml(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
        return config

def dump_yaml(config, path):
    with open(path, 'w') as file:
        yaml.dump(config, file)

def config_tsbs_load_for_greptime(config_path, input_file):
    if is_file_exists(config_path):
        # Config file already exists
        config = load_yaml(config_path)

        bench_config = BenchConfig(input_file)
        # Read bench config from file
        bench_config.read_from_config(config)

        return bench_config

    # Load template
    template_path = '%s/tsbs_load.template.yaml' % CONFIG_DIR
    config = load_yaml(template_path)

    # Overwrite template by default config.
    bench_config = BenchConfig(input_file)
    bench_config.write_to_config(config)

    # Write yaml to config_path
    dump_yaml(config, config_path)

    print('generate config to %s' % config_path)

    return bench_config

def bench_greptime(tsbs_load_greptime, bench_config):
    cmd = '%s --urls=%s --file=%s --batch-size=%s --gzip=%s --workers=%s' % (tsbs_load_greptime,
        bench_config.urls, bench_config.file, bench_config.batch_size, bench_config.gzip, bench_config.workers)
    run_cmd(cmd)

def generate(args):
    paths = WorkspacePaths(args.workspace)

    maybe_build_tsbs(paths)

    output_file = '%s/%s' % (paths.workspace, BENCH_DATA_FILE)
    if args.output_name is not None:
        output_file = '%s/%s' % (paths.workspace, args.output_name)

    if not is_file_exists(output_file):
        print('Try to generate data to %s' % output_file)
        generate_data(paths.data_generator_path, output_file)
    else:
        print('%s already exists' % output_file)

def greptime(args):
    paths = WorkspacePaths(args.workspace)

    maybe_build_tsbs(paths)

    input_file = '%s/%s' % (paths.workspace, BENCH_DATA_FILE)
    if args.input_name is not None:
        input_file = '%s/%s' % (paths.workspace, args.input_name)

    print('input file is %s' % input_file)
    bench_config = config_tsbs_load_for_greptime(paths.tsbs_load_greptime, input_file)

    bench_greptime(paths.tsbs_load_greptime, bench_config)

if __name__ == '__main__':
    # Instantiate the parser
    parser = argparse.ArgumentParser(prog='QuickTSBS', description='Quick TSBS Setup')
    parser.add_argument('--workspace', default=DEFAULT_WORKSPACE, help='workspace directory')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Parser for the "generate" command
    generate_parser = subparsers.add_parser('generate', help='generate help')
    generate_parser.add_argument('--output-name', help='output data file name')
    generate_parser.set_defaults(func=generate)

    # Parser for the "greptime" command
    greptime_parser = subparsers.add_parser('greptime', help='greptime help')
    greptime_parser.add_argument('--input-name', help='input data file name')
    greptime_parser.set_defaults(func=greptime)

    if len(sys.argv) == 1:
        parser.print_help()
        # parser.print_usage() # for just the usage line
        parser.exit()

    # Parse arguments
    args = parser.parse_args()
    args.func(args)
