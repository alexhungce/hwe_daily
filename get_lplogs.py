#!/usr/bin/python3
# Copyright (C) 2019-2021 Canonical
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys, os, launchpadlib, argparse
from launchpadlib.launchpad import Launchpad

cachedir = os.environ['HOME'] + "/.launchpadlib/cache/"

def no_credential():
    print("Can't proceed without Launchpad credential.")
    sys.exit()

launchpad = Launchpad.login_with('Daily_track', 'production', credential_save_failed=no_credential, version='devel')

def get_attachment(bug):

    print("Get logs for %s" % (bug.web_link))

    attachs = bug.attachments
    for attach in attachs:
        print("Downloading " + attach.title + "...")

        with open(attach.title, 'wb+') as f:
            f.write(attach.data.open().getvalue())
            f.close()

def main():

    myself = launchpad.me
    bugs_assigned = myself.searchTasks(assignee = myself)

    parser = argparse.ArgumentParser(description='Get attachments from Launchpad bug(s).')
    parser.add_argument("-n", "--bug_num", help="a Launchpad bug")
    parser.add_argument("-f", "--file", help="a list of Launchpad bugs ")
    args = parser.parse_args()

    if args.bug_num:
        bug = launchpad.bugs[args.bug_num]
        get_attachment(bug)
    if args.file:
        with open(args.file, "r") as bugs_list:
            bug_dir = "bug-logs"
            os.mkdir(bug_dir)
            os.chdir(bug_dir)
            for line in bugs_list:
                stripped = line.strip()
                os.mkdir(stripped)
                os.chdir(stripped)
                bug = launchpad.bugs[stripped]
                get_attachment(bug)
                os.chdir("..")

    return 0

if __name__ == "__main__":
    main()
