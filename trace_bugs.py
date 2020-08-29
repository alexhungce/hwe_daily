#!/usr/bin/python3
# Copyright (C) 2016-2020 Canonical
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

# key = bug number, value = date of last messenge
def get_bugs_lp(user):
    bugs_dict = {}

    bugs = user.searchTasks(assignee = user)

    for lp_bug in bugs:
        bug = launchpad.load(lp_bug.bug_link)
        bugs_dict.update({bug.id:str(bug.date_last_message)[:16]})

    return bugs_dict

def get_bugs_file(filename):
    bugs_dict = {}

    try:
        f = open(filename, "r")
    except IOError:
        f = open(filename, "w+")

    for line in f:
        line = line.strip()
        try:
            pos = line.index(" ")
        except:
            continue
        bugs_dict.update({int(line[:pos]):line[pos + 1:]})

    f.close()

    return bugs_dict

def print_updates(lp_dict, file_dict):

    new_dict = dict(set(lp_dict.items()) ^ set(file_dict.items()))

    for key in new_dict:
        diff = "*"

        if key not in lp_dict:
            diff = "-"
        elif key not in file_dict:
            diff = "+"

        bug = launchpad.bugs[key]
        print("  %s %d - %s [] | %s" % (diff, bug.id, bug.title, bug.web_link))


    return new_dict

def check_myself_updates(myself, updates_dict):

    for key in updates_dict:
        bug = launchpad.bugs[key]
        last_message = bug.messages_collection[bug.message_count - 1]
        if last_message.owner.name != myself.name:
            return False

    return True

def update_bug_to_file(filename, bugs_dict):

    f = open(filename, "w+")

    for key in bugs_dict:
        f.write(str(key) + " " + bugs_dict[key] + "\n")

    f.close()
    return

def main():

    myself = launchpad.me
    bugs_assigned = myself.searchTasks(assignee = myself)

    logfile = str(sys.argv[1])

    print('Hello, %s! Your bug number: %d' % (myself.display_name, bugs_assigned.total_size))

    lp_list = get_bugs_lp(myself)
    file_list = get_bugs_file(logfile)

    updates_dict = print_updates(lp_list, file_list)

    if len(updates_dict) != 0:
        update_bug_to_file(logfile, lp_list)

        if check_myself_updates(myself, updates_dict):
            return 100

        return 255

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
