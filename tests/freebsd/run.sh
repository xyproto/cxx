#!/usr/bin/env bash

scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

#vagrant-plugin-install() {
#  local plugin="$1"
#  msg2 "Installing the $plugin plugin, if not already installed"
#  vagrant plugin list | grep -q "$plugin" || vagrant plugin install "$plugin"
#}

main() {
#  msg2 'Listing Vagrant plugins'
#  vagrant plugin list
#
#  vagrant-plugin-install pkg-config
#  vagrant-plugin-install vagrant-libvirt
#
#  msg2 'Vagrant up'
#  vagrant up --provision --provider=libvirt
  vagrant up --provision
}

main "$@"
