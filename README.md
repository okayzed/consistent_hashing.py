# About

This code is an attempt at making consistent hashing in python.  Consistent
hashing consists of the idea is that you want to map resources -> servers, but
when you insert or remove a server, you want the majority of resources to stay
on the same server they were assigned to earlier.


## How it works

Each servers is inserted into a binary search tree, using the hash of the
server as its key. When looking for a resource, we find the server that is the
in-order successor to that resource's hash. If there is no successor, we return
the minimum value in the tree.

