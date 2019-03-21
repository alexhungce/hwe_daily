#!/usr/bin/python3
# Copyright (C) 2019 Canonical
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

import sys, os, launchpadlib
from launchpadlib.launchpad import Launchpad

cachedir = os.environ['HOME'] + "/.launchpadlib/cache/"

def no_credential():
    print("Can't proceed without Launchpad credential.")
    sys.exit()

launchpad = Launchpad.login_with('Daily_track', 'production', credential_save_failed=no_credential, version='devel')

def main():

    myself = launchpad.me
    bugs_assigned = myself.searchTasks(assignee = myself)

    bug = launchpad.bugs[sys.argv[1]]

    print("Get logs for %s" % (bug.web_link))

    attachs = bug.attachments
    for attach in attachs:
        print("Downloading " + attach.title + "...")

        with open(attach.title, 'wb+') as f:
            f.write(attach.data.open().getvalue())
            f.close()

    return 0

if __name__ == "__main__":
    main()
