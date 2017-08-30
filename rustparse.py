"""Parser for `cargo clippy` output"""

import sys
import os
import tempfile
import argparse
import json
import re


class JSONManager:
    def __init__(self, file):
        """Argument of type file object is required to be passed to JSON manager"""
        self.json_list = []
        self.filters = []
        self.file = file

        self._strip_json()

    def _strip_json(self):
        """Parse individual JSONs and pass them to manager"""
        self.file.seek(0)
        for line in self.file.readlines():
            if not re.match("{.*}", line):
                continue
            json_dict = json.loads(line)
            self.append(json_dict)

    def add_filter(self, json_filter, values):
        """Parses filter into Rust-like JSON format and adds it to filters"""
        if values is None:
            return
        for val in values.split(","):
            self.filters.append('"{}": (")?{}(")?'.format(json_filter, val))

    def apply_filters(self):
        """Process filters given by add_filter(...) function, removes items matching given filter"""
        if not len(self.filters):
            return
        new_list = []
        for j in self.json_list:
            if not self.is_filtered(json.dumps(j)):
                new_list.append(j)
        self.json_list = new_list

    def is_filtered(self, json_str):
        for f in self.filters:
            if re.search(f, json_str):
                return True

    def append(self, json_dict):
        self.json_list.append(json_dict)

    def dumps(self, file=sys.stdout):
        """Parse json to fit the desired output"""
        for obj in self.json_list:
            print(json.dumps(obj, indent=4), "\n", file=file)

    def dump_file(self, fpath, verbose=True):
        """Truncate (or create) file given by fpath and write dump json content"""
        with open(fpath, 'w') as f:
            self.dumps(file=f)
        if verbose:
            print("File {} has been dumped into {}".format(os.path.basename(fpath), os.path.dirname(fpath)),
                  file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("FILE", nargs='?', type=argparse.FileType('r'), default='-',
                        help="file in JSON format containing rust defects to be parsed")
    parser.add_argument("--filter-opt-level", help="comma separated list of values,"
                                               " filter out JSON items matching given opt-level")
    parser.add_argument("--filter-debuginfo", help="comma separated list of values, "
                                                   "filter out JSON items matching given debuginfo")
    parser.add_argument("--filter-reason", help="comma separated list of values,"
                                                " filter out JSON items matching given reason")
    parser.add_argument("--dump", nargs='?', const='json.dump', type=str,
                        help="dumps the parsed file into file DUMP (defaults to 'json.dump')")
    args = parser.parse_args()

    # Save the input into temporary file, so that we could check for size and seek later
    tmp_file = tempfile.TemporaryFile('r+')
    tmp_file.write(args.FILE.read())
    tmp_file.seek(0)

    # Close opened input stream
    path = args.FILE.name
    args.FILE.close()

    if args.verbose:
        print('Reading lines from input ...', file=sys.stderr)
    if 0 >= len(tmp_file.readlines()):
        print(os.path.basename(__file__), ": error: Empty input provided: %s" % os.path.abspath(path), file=sys.stderr)
        exit(1)

    manager = JSONManager(tmp_file)
    # Check if any filters are specified, if so, add them to the parser
    manager.add_filter("opt_level", args.filter_opt_level)
    manager.add_filter("debuginfo", args.filter_debuginfo)
    manager.add_filter("reason", args.filter_reason)

    manager.apply_filters()

    if args.dump is not None:
        manager.dump_file(args.dump, args.verbose)
    else:
        manager.dumps()

    tmp_file.close()

if __name__ == '__main__':
    main()
