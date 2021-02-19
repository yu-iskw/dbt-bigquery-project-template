#!/bin/bash
set -e

# Check unsecure python modules.
safety check

NUM_UNSECURE_MODULE=$(safety check --bare | wc -l)
if [[ $NUM_UNSECURE_MODULE -ne 0 ]] ; then
  exit 1
fi