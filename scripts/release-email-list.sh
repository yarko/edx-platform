#! /bin/bash

LOG_SPEC="$1..$2"

echo $(git log $LOG_SPEC --format='format:"%an <%ae>"' --no-merges | sort -u | sed 's/$/,/g')

IFS=$'\n'
for NAME in $(git log $LOG_SPEC --format='tformat:%an' --no-merges | sort -u); do
    echo $NAME
    git --no-pager log $LOG_SPEC --format='tformat:    %s - https://github.com/edx/edx-platform/commit/%h' --author="$NAME" --no-merges
done