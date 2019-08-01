#!/bin/bash
# Copyright (C) 2016-2019 Canonical
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

BACKUP_DIR="$HOME/Dropbox/canonical/launchpad"
BUGS_FILE="bugs_yesterday.log"

while true ; do

	date "+%F %r"

	[ -d $BACKUP_DIR ] && cp -f ${BACKUP_DIR}/${BUGS_FILE} .
	./trace_bugs.py ${BUGS_FILE}
	ret=$?
	if [ $ret -eq 0 ] ; then
		read -t 900 -p "No updates for launchpad bugs. Wait for 15 mins or continue by [Enter]..."
		printf "\n\n"
	elif [ $ret -eq 100 ] ; then
		echo "Launchpad updates are by $(whoami)..."
		[ -d $BACKUP_DIR ] || continue
		diff ${BUGS_FILE} ${BACKUP_DIR}/${BUGS_FILE} &> /dev/null
		if [ $? -ne 0 ] ; then
			cp ${BUGS_FILE} ${BACKUP_DIR}/${BUGS_FILE}
			echo "Update log file ${BUGS_FILE} to backup directory..."
			echo ""
		fi
	elif [ $ret -eq 255 ] ; then
		notify-send "Launchpad updates are available!"
		echo ""
		read -p "Press [Enter] to continue..."

		[ -d $BACKUP_DIR ] || continue
		diff ${BUGS_FILE} ${BACKUP_DIR}/${BUGS_FILE} &> /dev/null
		if [ $? -ne 0 ] ; then
			cp ${BUGS_FILE} ${BACKUP_DIR}/${BUGS_FILE}
			echo "Update log file ${BUGS_FILE} to backup directory..."
			echo ""
		fi
	else
		exit
	fi
done
