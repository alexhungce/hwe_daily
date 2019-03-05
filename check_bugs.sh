#!/bin/bash

DROPBOX_DIR="$HOME/Dropbox/canonical/launchpad"
PROJECT_FILES=( "bugs_yesterday.log" )
BUGS_FILE="bugs_yesterday.log"

while true ; do

	cp -f ${DROPBOX_DIR}/${BUGS_FILE} .
	./lp_bugs_tracer.py
	ret=$?
	if [ $ret -eq 0 ] ; then
		read -t 900 -p "No updates for launchpad bugs. Wait for 15 mins or continue by [Enter]..."
		printf "\n\n"
	elif [ $ret -eq 255 ] ; then
		notify-send "Launchpad updates are available!"
		echo ""
		read -p "Press [Enter] to continue..."

		diff ${BUGS_FILE} ${DROPBOX_DIR}/${BUGS_FILE} >> /dev/null
		if [ $? -ne 0 ] ; then
			cp ${BUGS_FILE} ${DROPBOX_DIR}/${BUGS_FILE}
			echo "Update log file ${BUGS_FILE} to Dropbox..."
			echo ""
		fi
	else
		exit
	fi
done
