#!/bin/sh
quit() {
  echo "$1"
  exit 1
}
lighttpd -v 2>/dev/null >/dev/null || quit 'This script requires lighttpd'
test -f ./fastcgi || quit 'This script requires ./fastcgi'
rm -f /tmp/hello.socket*
echo
echo 'Serving the FastCGI program at http://localhost:5000/'
echo
lighttpd -D -f serve.conf
