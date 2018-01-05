#!/usr/bin/env bash
set -i

cur_dir="$(pwd)"
root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
examples_dir="$root_dir/../examples"
figlet=$(which figlet 2>/dev/null || echo)
cmds="clean build"
args=

which scons 2>/dev/null
which make 2>/dev/null
sm version

if [ "$1" == run ]; then
  # Also run if "run" was given
  cmds="$cmds run"
  shift
  args="$@"
elif [ "$1" == rebuild ]; then
  # Only rebuild if "rebuild" was given
  cmds="rebuild"
  shift
  args="$@"
elif [ "$1" == fastbuild ] || [ "$1" == fast ]; then
  cmds="fastclean build"
  shift
  args="$@"
elif [ "$1" != build ] && [ "$1" != "" ]; then
  cmds="$@"
fi

# Perform all commands
for cmd in $cmds; do
  msg="Building all examples"
  if [ "$cmd" == clean ]; then
    msg="Cleaning all examples"
  elif [ "$cmd" == run ]; then
    msg="Running all examples"
  elif [ "$cmd" == rebuild ]; then
    msg="Rebuilding all examples"
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
    if [ $cmd == clean -o $cmd == fastclean ]; then
      # without $args when cleaning
      echo sm -C "$rel_dir" $cmd
      sm -C "$rel_dir" $cmd
    elif [ $cmd != build ]; then
      # with both $cmd and $args
      echo sm -C "$rel_dir" $cmd $args
      sm -C "$rel_dir" $cmd $args
    else
      # without $cmd
      echo sm -C "$rel_dir" $args
      sm -C "$rel_dir" $args
    fi
    echo
  done
done
