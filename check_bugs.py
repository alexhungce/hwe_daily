#!/usr/bin/python3
# Copyright (C) 2016-2021 Canonical
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

import sys, os, argparse
from launchpadlib.launchpad import Launchpad
from select import select
from getpass import getuser
from subprocess import run
from datetime import datetime
from filecmp import cmp
from pathlib import Path
from shutil import copyfile

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

def trace_bugs(logfile):

    myself = launchpad.me
    bugs_assigned = myself.searchTasks(assignee = myself)

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

def update_to_dest(bug_file, backup_dir):

    if backup_dir == None:
        return

    dir = os.environ['HOME'] + "/" + backup_dir
    if not os.path.exists(dir):
        return

    dest = dir + "/" + bug_file
    if not cmp(bug_file, dest):
        print("Update log file " + bug_file + " to backup directory...")
        copyfile(bug_file, dest)

def process_results(bug_file, backup_dir):

    result = trace_bugs(bug_file)
    if result == 0:
        print ("No updates for launchpad bugs. Wait for 15 mins or continue by [Enter]...")
        i, o, e = select( [sys.stdin], [], [], 900)
        if (i):
            sys.stdin.readline().strip()
    elif result == 100:
        print ("Launchpad updates are by " + getuser()  + "...")
    elif result == 255:
        run(['notify-send', 'Launchpad updates are available!'])
        input("Press [Enter] to continue...")
    else:
        run(['notify-send', 'Something went wrong... Exiting launchpad_bugs!'])

    update_to_dest(bug_file, backup_dir)

def main():

    parser = argparse.ArgumentParser(description='Check the updates of assigned bugs.')
    parser.add_argument("-f", "--file", help="bug list", required=True)
    parser.add_argument("-d", "--dir", help="sync dir - 'launchpad' when in $HOME/launchpad")
    args = parser.parse_args()

    while True:
        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
        process_results(args.file, args.dir)

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
