#!/usr/bin/env python3
import os

import glob
import re

path_split_re = re.compile(r'^/proc/([^/]+)/fd/([^/]+)$')

fdinfo_pos_re = re.compile(r'^pos:\s+(\d+)$')

# we only want real files
target_fd_exclusion_re = re.compile(r'^(/dev/|/proc/)')

# all processes' open files are found in /proc/<pid>/fd/<n>
# and the current seek position can be found in /proc/<pid>/fdinfo/<n>
# this collects real open files and calcs the percent seek
# useful for checking progress of long-running processes working (linearly) on large files
# only shows files and processes the current user has access to
# 
# 
# todo: organize by pid and show full proc name or command line
# todo: hide files at 100% (that will exclude some noise (open files that aren't interesting))

class OpenFile(object):
    def __init__(self, proc, fd, filepath, target_path):
        self.proc = proc
        self.fd = fd
        self.filepath = filepath
        self.target_path = target_path
        self.total_size = self.calc_total_size()


    def calc_total_size(self):
        return os.path.getsize(self.filepath)

    @property
    def fdinfo_path(self):
        return '/proc/%s/fdinfo/%s' % (self.proc, self.fd)

    def calc_processed_size(self):
        with open(self.fdinfo_path, 'r') as f:
            for row in f:
                match = fdinfo_pos_re.match(row)
                if match:
                    return int(match.group(1), 10)

    @property
    def processed_size(self):
        return self.calc_processed_size()

def process():
    file_paths = glob.iglob('/proc/*/fd/*')

    collected = []

    for file_path in file_paths:
        if os.path.islink(file_path):
            target_path = os.path.realpath(file_path)

            if target_fd_exclusion_re.match(target_path):
                # we only want real files
                continue

            path_parts = path_split_re.match(file_path)

            if path_parts:
                proc = path_parts.group(1)
                fd = path_parts.group(2)

                collected.append(OpenFile(proc, fd, file_path, target_path))

    return collected

if __name__ == '__main__':
    files = process()

    for file in files:
        try:
            print('%s: %d of %d (%d%%)' % (
                file.target_path,
                file.processed_size,
                file.total_size,
                file.processed_size / file.total_size * 100
            ))
        except ZeroDivisionError:
            # not interested in files with total size = 0
            pass
