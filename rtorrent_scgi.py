#!/usr/bin/python

# rtorrent_xmlrpc
# (c) 2011 Roger Que <alerante@bellsouth.net>
# Ported to python3 by John Hochstetler
# Based partially on Daniel Bowring's python3 port:
# https://github.com/dbowring/rtorrent_xmlrpc
# However this port maintains urllib URI parsing like the original
#
# Python module for interacting with rtorrent's XML-RPC interface
# directly over SCGI, instead of through an HTTP server intermediary.
# Inspired by Glenn Washburn's xmlrpc2scgi.py [1], but subclasses the
# built-in xmlrpc.client classes so that it is compatible with features
# such as MultiCall objects.
#
# [1] <http://libtorrent.rakshasa.no/wiki/UtilsXmlrpc2scgi>
#
# Usage: server = SCGIServerProxy('scgi://localhost:7000/')
#        server = SCGIServerProxy('scgi:///path/to/scgi.sock')
#        print(server.system.listMethods()) # single call
#        multicall = xmlrpc.client.MultiCall(server) #multicall
#        multicall.get_up_rate()
#        multicall.get_down_rate()
#        print(multicall())
#
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the
# OpenSSL library under certain conditions as described in each
# individual source file, and distribute linked combinations
# including the two.
#
# You must obey the GNU General Public License in all respects for
# all of the code used other than OpenSSL.  If you modify file(s)
# with this exception, you may extend this exception to your version
# of the file(s), but you are not obligated to do so.  If you do not
# wish to do so, delete this exception statement from your version.
# If you delete this exception statement from all source files in the
# program, then also delete it here.
#
#
#
# Portions based on Python's xmlrpclib:
#
# Copyright (c) 1999-2002 by Secret Labs AB
# Copyright (c) 1999-2002 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

import re
import socket
import urllib.parse
import collections
import xmlrpc.client

NULL = b'\x00'


class SCGITransport(xmlrpc.client.Transport):
    def _build_scgi_request(self, request_body):
        # an ordered dict from a set of sets so that content length is always the first
        # key present, and keys are guaranteed to be unique
        headers = collections.OrderedDict((
            (b'CONTENT_LENGTH', str(len(request_body)).encode('utf-8')),
            (b'SCGI', b'1')
        ))
        encoded_header = NULL.join(k + NULL + v for k, v in headers.items()) + NULL
        header_length = str(len(encoded_header)).encode('utf-8')
        return header_length + b':' + encoded_header + b',' + request_body

    def single_request(self, host, handler, request_body, verbose=0):
        # Add SCGI headers to the request.
        scgi_request = self._build_scgi_request(request_body)
        sock = None
        try:
            if host:
                host, port = urllib.parse.splitport(host)
                addrinfo = socket.getaddrinfo(host, port, socket.AF_INET,
                                              socket.SOCK_STREAM)
                sock = socket.socket(*addrinfo[0][:3])
                sock.connect(addrinfo[0][4])
            else:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(handler)

            self.verbose = verbose

            sock.send(scgi_request)
            return self.parse_response(sock.makefile())
        finally:
            if sock:
                sock.close()

    def parse_response(self, response):
        p, u = self.getparser()

        response_body = ''
        while True:
            data = response.read(1024)
            if not data:
                break
            response_body += data

        # Remove SCGI headers from the response.
        try:
            scgi_header, xmlrpc_body = re.split(r'\n\s*?\n', response_body, maxsplit=1)
        except ValueError:
            raise xmlrpc.client.ResponseError("Could not find response body.")

        if self.verbose:
            print('body:', repr(xmlrpc_body))

        p.feed(xmlrpc_body)
        p.close()

        return u.close()


class SCGIServerProxy(xmlrpc.client.ServerProxy):
    def __init__(self, uri, transport=None, encoding=None, verbose=False, allow_none=False, use_datetime=False,
                 use_builtin_types=False):
        scheme, uri = urllib.parse.splittype(uri)
        if scheme != 'scgi':
            raise OSError('unsupported XML-RPC protocol')

        if transport is None:
            transport = SCGITransport(use_datetime=use_datetime,
                                      use_builtin_types=use_builtin_types)

        super().__init__(uri='http:placeholder', transport=transport, encoding=encoding, verbose=verbose,
                         allow_none=allow_none, use_datetime=use_datetime, use_builtin_types=use_builtin_types)

        # circumvent name-mangling to set host and path after super() in order to avoid super() checking the URI scheme.
        # See also: https://docs.python.org/3/tutorial/classes.html#private-variables
        self._ServerProxy__host, self._ServerProxy__handler = urllib.parse.splithost(uri)
        if not self._ServerProxy__handler:
            self._ServerProxy__handler = '/'
