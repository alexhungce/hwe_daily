#!/usr/bin/python
import sys
import launchpadlib
from launchpadlib.launchpad import Launchpad

cachedir = "/home/alexhung/.launchpadlib/cache/"
logfile = "bugs_yesterday.log"

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

    f = open(filename, "r")

    for line in f:
        line = line.strip()
        try:
            pos = line.index(" ")
        except:
            continue
        bugs_dict.update({int(line[:pos]):line[pos + 1:]})

    f.close()

    return bugs_dict

def print_updates(new_dict):

    for key in new_dict:
        bug = launchpad.bugs[key]
        print(" * %d - %s [] | %s" % (bug.id, bug.title, bug.web_link))

def update_bug_to_file(filename, bugs_dict):

    f = open(filename, "w+")

    for key in bugs_dict:
        f.write(str(key) + " " + bugs_dict[key] + "\n")

    f.close()
    return

def main():

    myself = launchpad.me
    bugs_assigned = myself.searchTasks(assignee = myself)

    print('Hello, %s! Your bug number: %d' % (myself.display_name, bugs_assigned.total_size))
    print("")

    lp_list = get_bugs_lp(myself)
    file_list = get_bugs_file(logfile)
    updates_dict = dict(set(lp_list.items()) ^ set(file_list.items()))

    print_updates(updates_dict)

    if len(updates_dict) != 0:
        update_bug_to_file(logfile, lp_list)
        return 255

    return 0

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)