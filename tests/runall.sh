#!/bin/bash
cur_dir="$(pwd)"
root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
examples_dir="$root_dir/../examples"
figlet=$(which figlet)

for cmd in clean build run; do
  msg="Building all examples"
  if [ "$cmd" == clean ]; then
    msg="Cleaning all examples"
  elif [ "$cmd" == run ]; then
    msg="Running all examples"
  fi
  if [ ! $figlet == "" ]; then
    figlet -f small "$msg"
    echo
  else
    echo -e '|\n|'
    echo "|  $msg..."
    echo -e '|\n|'
  fi
  for example_dir in "$examples_dir"/*; do
    rel_dir="$(realpath --relative-to="$cur_dir" "$example_dir")"
    echo "------- $rel_dir -------"
    if [ $cmd != build ]; then
      echo sm -C "$rel_dir" $cmd
      sm -C "$rel_dir" $cmd
    else
      echo sm -C "$rel_dir"
      sm -C "$rel_dir"
    fi
    echo
  done
done
