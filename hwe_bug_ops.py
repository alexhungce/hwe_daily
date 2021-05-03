#!/usr/bin/python3
# Copyright (C) 2021 Canonical
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

class Lp_Op(object):

    def __init__(self):
        self.launchpad = Launchpad.login_with('Daily_track', 'production',
            credential_save_failed=self.no_credential, version='devel')
        self.myself = self.launchpad.me
        self.bugs_assigned = self.myself.searchTasks(assignee = self.myself)

    def no_credential(self):
        print("Can't proceed without Launchpad credential.")
        sys.exit()

    def get_attachment(self, bug_num):
        bug = self.launchpad.bugs[bug_num]
        print("Get logs for %s" % (bug.web_link))
        attachs = bug.attachments
        for attach in attachs:
            print("Downloading " + attach.title + "...")

            with open(attach.title, 'wb+') as f:
                f.write(attach.data.open().getvalue())
                f.close()

    def get_attachment_file(self, file, bug_dir):
        with open(file, "r") as bugs_list:
            if bug_dir == None:
                bug_dir = "bug-logs"

            os.mkdir(bug_dir)
            os.chdir(bug_dir)

            for line in bugs_list:
                stripped = line.strip()
                os.mkdir(stripped)
                os.chdir(stripped)
                self.get_attachment(stripped)
                os.chdir("..")

    def process_results(self, bug_file, backup_dir):
        result = self.__trace_bugs(bug_file)
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

        self.__update_to_dest(bug_file, backup_dir)

    def __get_bugs_lp(self, user):
        # key = bug number, value = date of last messenge
        bugs_dict = {}
        bugs = user.searchTasks(assignee = user)

        for lp_bug in bugs:
            bug = self.launchpad.load(lp_bug.bug_link)
            bugs_dict.update({bug.id:str(bug.date_last_message)[:16]})

        return bugs_dict

    def __get_bugs_file(self, filename):
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

    def __print_updates(self, lp_dict, file_dict):
        new_dict = dict(set(lp_dict.items()) ^ set(file_dict.items()))
        for key in new_dict:
            diff = "*"

            if key not in lp_dict:
                diff = "-"
            elif key not in file_dict:
                diff = "+"

            bug = self.launchpad.bugs[key]
            print("  %s %d - %s [] | %s" % (diff, bug.id, bug.title, bug.web_link))

        return new_dict

    def __check_myself_updates(self, updates_dict):
        for key in updates_dict:
            bug = self.launchpad.bugs[key]
            last_message = bug.messages_collection[bug.message_count - 1]
            if last_message.owner.name != self.myself.name:
                return False

        return True

    def __update_bug_to_file(self, filename, bugs_dict):
        f = open(filename, "w+")
        for key in bugs_dict:
            f.write(str(key) + " " + bugs_dict[key] + "\n")

        f.close()
        return

    def __trace_bugs(self, logfile):
        print('Hello, %s! Your bug number: %d'
            % (self.myself.display_name, self.bugs_assigned.total_size))

        lp_list = self.__get_bugs_lp(self.myself)
        file_list = self.__get_bugs_file(logfile)

        updates_dict = self.__print_updates(lp_list, file_list)

        if len(updates_dict) != 0:
            self.__update_bug_to_file(logfile, lp_list)

            if self.__check_myself_updates(updates_dict):
                return 100
            return 255

        return 0

    def __update_to_dest(self, bug_file, backup_dir):
        if backup_dir == None:
            return

        dir = os.environ['HOME'] + "/" + backup_dir
        if not os.path.exists(dir):
            return

        dest = dir + "/" + os.path.basename(bug_file)
        if not cmp(bug_file, dest):
            print("Update log file " + bug_file + " to backup directory...")
            copyfile(bug_file, dest)

def main():
    parser = argparse.ArgumentParser(description='Check the updates of assigned bugs.')
    parser.add_argument("-g", "--getAttachment", help="Get attachments from a Launchpad bug")
    parser.add_argument("-f", "--file", help="Check the updates of assigned bugs")
    parser.add_argument("-d", "--dir", help="Backup dir - 'backup' when in $HOME/backup")
    args = parser.parse_args()

    operation = Lp_Op()
    if args.getAttachment != None:
        if os.path.isfile(args.getAttachment) == False:
            ''' Download attachments from a launchpad bug
                ex. hwe_bug_ops.py -g 100 # downloads attachments from LP:100
            '''
            operation.get_attachment(args.getAttachment)
        else:
            ''' Download all attachments from launchpad bugs listed in a file
                ex. hwe_bug_ops.py -g bugs.lst # downloads attachments listed in bugs.lst
                where bugs.lst contains bug numbers:
                123
                456
            '''
            operation.get_attachment_file(args.getAttachment, args.dir)

    elif args.file != None:
        ''' Check the status of assigned launchpad bugs (every 15 mins)
            ex. hwe_bug_ops.py -f bugs_yesterday.log    # no backup
                hwe_bug_ops.py -f bugs_yesterday.log -d Documents/bug_backup
        '''
        while True:
            print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
            operation.process_results(args.file, args.dir)

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
