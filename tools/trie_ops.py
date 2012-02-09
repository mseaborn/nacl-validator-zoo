# Copyright (c) 2012 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from memoize import Memoize
import trie


def FlattenTrie(node, bytes=[]):
  if node.accept:
    yield bytes
  for byte, next in sorted(node.children.iteritems()):
    for result in FlattenTrie(next, bytes + [byte]):
      yield result


@Memoize
def Subtract(node1, node2):
  if node1 == trie.EmptyNode:
    return trie.EmptyNode
  if node2 == trie.EmptyNode:
    return node1
  if node1 == node2:
    return trie.EmptyNode
  keys = set()
  keys.update(node1.children.iterkeys())
  keys.update(node2.children.iterkeys())
  children = {}
  for key in keys:
    child = Subtract(node1.children.get(key, trie.EmptyNode),
                     node2.children.get(key, trie.EmptyNode))
    if child != trie.EmptyNode:
      children[key] = child
  return trie.MakeInterned(children, node1.accept and not node2.accept)


# Introduce wildcard bytes into a trie where the wildcard bytes have
# previously been expanded out.
@Memoize
def Simplify(node):
  dests = set(node.children.itervalues())
  if (len(dests) == 1 and
      len(set(node.children.iterkeys())) == 256):
    keys = sorted(node.children.iterkeys())
    assert keys == ['%02x' % c for c in range(256)], keys
    children = {'XX': Simplify(list(dests)[0])}
  else:
    children = node.children
  return trie.MakeInterned(dict((key, Simplify(value))
                                for key, value in children.iteritems()),
                           node.accept)
