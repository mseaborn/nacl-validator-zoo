# Copyright (c) 2011 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import weakref

import memoize


class Trie(object):

  def __init__(self, children, accept):
    self.children = children
    self.accept = accept


interned = weakref.WeakValueDictionary()

def MakeInterned(children, accept):
  key = (accept, tuple(sorted(children.iteritems())))
  node = interned.get(key)
  if node is None:
    node = Trie(children, accept)
    interned[key] = node
  return node


EmptyNode = MakeInterned({}, False)
AcceptNode = MakeInterned({}, True)


def GetAllNodes(root):
  node_list = []
  node_set = set()
  def Recurse(node):
    if node not in node_set:
      node_list.append(node)
      node_set.add(node)
      for key, child in sorted(node.children.iteritems()):
        Recurse(child)
  Recurse(root)
  return node_list


def TrieToDict(root):
  node_list = GetAllNodes(root)
  # We stringify the IDs because JSON requires dict keys to be strings.
  node_to_id = dict((node, str(index)) for index, node in enumerate(node_list))
  return {'start': node_to_id[root],
          'map': dict((node_to_id[node],
                       dict((key, node_to_id[dest])
                            for key, dest in node.children.iteritems()))
                      for node in node_list),
          'accepts': dict((node_to_id[node], node.accept)
                          for node in node_list)}


def TrieFromDict(trie_data):
  @memoize.Memoize
  def MakeNode(node_id):
    children = dict(
        (key, MakeNode(child_id))
        for key, child_id in trie_data['map'][node_id].iteritems())
    return MakeInterned(children, trie_data['accepts'][node_id])

  return MakeNode(trie_data['start'])


def WriteToFile(output_filename, root):
  fh = open(output_filename, 'w')
  json.dump(TrieToDict(root), fh, sort_keys=True)
  fh.close()


def TrieFromFile(filename):
  fh = open(filename, 'r')
  trie_data = json.load(fh)
  fh.close()
  return TrieFromDict(trie_data)
