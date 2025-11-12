#!/usr/bin/env python3

from pathlib import Path
import sys
import argparse
import os
import glob
from cb_bsdl_parser import CBBsdl
from cb_bsdl_parser.cb_bsdl import SkipError
from cb_logging import CBLogger

from cb_bsdl_parser import __version__ as cb_bsdl_parser_version

LOG_FILE_NAME = 'cb_jtag_tool.log'


def run_test(test, msg, log):
    try:
        test()
        log.info(f'   {msg}: PASS')
    except ValueError as e:
        log.error(f'  {msg}: FAIL ({e})')
        return 1
    except SkipError as e:
        log.warning(f'  {msg}: SKIPPED ({e})')
    return 0


def check(bsdl: CBBsdl, log):
    ec = 0

    ec += run_test(bsdl.check_entity_name,
                   'Entity name check', log)
    ec += run_test(bsdl.check_bsr_length,
                   'BSR length check', log)
    ec += run_test(bsdl.check_ports_and_pin_map_length,
                   'Ports and pin map length check', log)
    ec += run_test(bsdl.check_port_to_pin_mapping,
                   'Port to pin mapping check', log)
    ec += run_test(bsdl.check_pin_to_port_mapping,
                   'Pin to port mapping check', log)
    ec += run_test(bsdl.check_bsr_to_ports_mapping,
                   'BSR to ports mapping check', log)
    ec += run_test(bsdl.check_pin_count,
                   'Pin count check', log)
    ec += run_test(bsdl.check_missing_pins,
                   'Missing pins check', log)
    ec += run_test(bsdl.check_extra_pins,
                   'Extra pins check', log)
    ec += run_test(bsdl.check_double_assigned_pins,
                   'Double assigned pins check', log)

    if ec > 0:
        log.error(f'  FAIL - Total errors in file: {ec}')
    else:
        log.info('   PASS - All good with this file!')

    return ec


def process_folder(folder, log):
    # Process all BSDL files in the folder

    log.info(f'Starting to process BSDL files in folder: {folder}')

    # if not os.path.isdir(folder_path):
    if not folder.is_dir():
        log.critical(f"Folder does not exist: {folder}")
        sys.exit(1)

    # Find all BSDL files (common extensions: .bsd, .bsdl)
    bsdl_patterns = [
        os.path.join(folder, "*.bsd"),
        os.path.join(folder, "*.bsdl"),
        os.path.join(folder, "*.BSL"),
        os.path.join(folder, "*.BSDL")
    ]

    bsdl_files = []
    for pattern in bsdl_patterns:
        bsdl_files.extend(glob.glob(pattern))

    if not bsdl_files:
        log.error(f'No BSDL files found in folder: {folder}')
        sys.exit(1)

    log.info(f'Found {len(bsdl_files)} BSDL files in {folder}')

    error_count = 0
    for bsdl_file in sorted(bsdl_files):
        error_count += process_file(bsdl_file, log)

    log.info('---------------------------------------------'
             '---------------------------------------------')
    log.info(f'Finished processing of {len(bsdl_files)} files in {folder}')
    if error_count > 0:
        log.error(f'  FAIL - Total errors found: {error_count}')
    else:
        log.info('   PASS - All good with these files!')


def process_file(bsdl_file, log):
    log.info(f'Starting to process BSDL file: {bsdl_file}')

    log.info('---------------------------------------------'
             '---------------------------------------------')
    log.info(f'Processing file: {bsdl_file}')
    try:
        bsdl = CBBsdl(bsdl_file, run_checks=False)
        error_count = check(bsdl, log)
    except Exception as e:
        log.critical(f'  Error processing {bsdl_file}: {e}')
        error_count = 1

    return error_count


def main():
    parser = argparse.ArgumentParser(
        description='Process a BSDL file.',
        usage='%(prog)s <bsdl_file> [options]')
    parser.add_argument('bsdl_file', type=str, nargs='?',
                        help='Path to the BSDL file')
    parser.add_argument('--folder', type=Path,
                        help='Path to folder containing BSDL files')
    parser.add_argument('-l', '--log', action='store_true',
                        help='Enable logging to file')

    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()

    # Validate that either bsdl_file or folder is provided, but not both
    if not args.bsdl_file and not args.folder:
        parser.error("Either provide a BSDL file or use --folder option")

    if args.bsdl_file and args.folder:
        parser.error(
            'Cannot specify both bsdl_file and'
            ' --folder. Use one or the other.')

    # store log file into parent dir of folder and name it
    # after the folder or after the bsdl_file name
    if args.folder:
        log_folder = args.folder.parent
        folder_name = args.folder.name
        log_file = os.path.join(log_folder, f'{folder_name}_check.log')
    else:
        log_file = args.bsdl_file + '_check.log'

    log = CBLogger(log_to_file=args.log,
                   log_file_name=log_file)

    log.info('Bonjour! - cb_bsdl_check')
    log.info(f'cb_bsdl_parser Version: {str(cb_bsdl_parser_version)}')
    log.info(f'Sys Platform: {sys.platform}')
    log.info(f'Python Version: {sys.version}')
    log.info(f'Command line arguments: {args}')
    log.info(f'Logging to file: {log_file}')

    # Process files based on input type
    if args.folder:
        process_folder(args.folder, log)
    else:
        # Process single file
        # bsdl = CBBsdl(args.bsdl_file, run_checks=False)
        # check(bsdl, log)

        process_file(args.bsdl_file, log)


if __name__ == '__main__':  # pragma: no cover
    main()
