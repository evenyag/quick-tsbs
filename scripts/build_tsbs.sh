#!/usr/bin/env bash

# Build tsbs
#
# Arguments:
# $1: tsbs source directory path
# $2: binary output directory path

set -x

# Create binary output directory if not exists.
mkdir -p $2
# Enter tsbs source directory.
pushd $1
# Build tsbs.
make -j4
# Move all binaries to target directory.
mv ./bin/* $2
# Remove bin directory
rmdir ./bin
# Exit tsbs directory.
popd
