#!/usr/bin/bash

for f in $1/out_*.file; do
    ${SeekerPath}/bin/coll $f $2 $3
    sleep 0.2
done
