#!/bin/bash -e

cur_dir="$(pwd)"
root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
examples_dir="$root_dir/../examples"
figlet=$(which figlet || echo)
cmds="clean build"

# Also run if "run" was given
if [ "$1" = "run" ]; then
  cmds="$cmds run"
fi

# Perform all commands
for cmd in $cmds; do
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
    rel_dir="$(realpath --relative-to="$cur_dir" "$example_dir" 2>/dev/null || echo $example_dir)"
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
