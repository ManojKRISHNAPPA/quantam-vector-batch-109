#!/bin/bash
for dir in shell git jenkins docker terraform ansible kubernetes
do
  echo "Installing $dir"
  mkdir $dir
  touch $dir/README.md
done

