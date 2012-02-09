# Copyright (c) 2012 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import optparse
import sys

import trie
import trie_ops


def Main(args):
  parser = optparse.OptionParser(usage='%prog [options] filename...')
  parser.add_option('--sub', '--subtract', dest='subtract',
                    default=[], action='append',
                    help='Filename of DFA to subtract')
  options, args = parser.parse_args(args)
  if len(args) == 0:
    parser.error('Expected some filename arguments')

  subtract_nodes = map(trie.TrieFromFile, options.subtract)

  for filename in args:
    node = trie.TrieFromFile(filename)
    for sub in subtract_nodes:
      node = trie_ops.Subtract(node, sub)
    for bytes in trie_ops.FlattenTrie(trie_ops.Simplify(node)):
      print ' '.join(bytes)


if __name__ == '__main__':
  Main(sys.argv[1:])
