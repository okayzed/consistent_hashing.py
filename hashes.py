import json
import sys

from collections import defaultdict

modulo = 1e7+9

class BinaryTree:
    def __init__(self, val=None, h=None):
        self.left = None
        self.right = None
        self.hash = None
        self.values = []
        self.parent = None

        self.insertions = []
        if val is not None:
            if h is None:
                h = hash(val)
            self.hash = h
            self.values.append(val)
            self.insertions.append([val, h])

    def to_string(self):
        return json.dumps(self.insertions)

    @classmethod
    def from_string(cls, s):
        insertions = json.loads(s)
        bt = BinaryTree(*insertions[0])

        for val, h in insertions[1:]:
            bt.add_value(val, h)

        return bt


    def add_value(self, value, h=None):
        if h is None:
            h = hash(value)

        if not self.hash:
            self.hash = h
            self.values = [value]
        else:
            self.__insert_node(value, h)

        self.insertions.append([value, h])

    # TODO: if we run into the same value again, we need to remove it
    # if value is not None, we will replace any node we find along the way too
    def remove(self, value=None):
        # remove the node
        if self.left and self.right:
            s = self.find_successor(self.hash, cyclic=False)
            # if there is no successor, we just remove this node and
            # don't bother swapping it with another node
            if not s:
                if self.parent.left == self:
                    self.parent.left = None
                elif self.parent.right == self:
                    self.parent.right = None

                return
            if s.hash > self.hash:
                self.values = s.values
                self.hash = s.hash
                s.remove()

        elif self.left:
            self.values = self.left.values
            self.hash = self.left.hash
            self.left.remove()

        elif self.right:
            self.values = self.right.values
            self.hash = self.right.hash
            self.right.remove()
        else:
            if self.parent.left == self:
                self.parent.left = None
            elif self.parent.right == self:
                self.parent.right = None

        # if we replaced our node with the same value we are replacing,
        # then we remove this node too
        if value in self.values:
            self.values.remove(value)

            if not self.values:
                self.remove(value)

    def remove_value(self, value):
        # for each node in the tree that has that value, we need to remove that node

        # to remove a node:
        # if node has two children:
        #   find successor and replace node value with successor's value
        # if node has one child:
        #   replace node value with its child value

        def visit_and_remove(node, value):
            if not node:
                return

            if value in node.values:
                node.values.remove(value)
                if not node.values:
                    node.remove(value)

            visit_and_remove(node.left, value)
            visit_and_remove(node.right, value)
        visit_and_remove(self, value)
        self.insertions = filter(lambda w: w[0] != value, self.insertions)


    def find_successor(self, h, cyclic=True):
        h = h % modulo
        if h > self.hash:
            if self.right:
                return self.right.find_successor(h, cyclic)
            else:
                return self.__successor(cyclic)

        if h == self.hash:
            return self.__successor(cyclic)

        if h < self.hash:
            if self.left:
                return self.left.find_successor(h, cyclic)
            else:
                return self


    def __insert_node(self, value, h=None):
        if self.hash == h:
            self.values.append(value)
            return

        if self.hash > h:
            if self.left:
                self.left.__insert_node(value, h)
            else:
                self.left = BinaryTree(value, h)
                self.left.parent = self

        if self.hash < h:
            if self.right:
                self.right.__insert_node(value, h)
            else:
                self.right = BinaryTree(value, h)
                self.right.parent = self

    def __find_min(self):
        if self.left:
            return self.left.__find_min()

        return self

    def __find_max(self):
        if self.right:
            return self.right.__find_max()
        return self

    def __successor(self, cyclic):
        # if there is a right child, we find min key in there
        # otherwise, we travel upwards until we find when
        # node is left child
        if self.right:
            return self.right.__find_min()

        cur = self
        parent = cur.parent
        while parent and cur:
            if cur == parent.left:
                return parent

            cur = cur.parent
            parent = cur.parent

        while cur:
            prev = cur
            cur = cur.parent

        if cyclic:
            return prev.__find_min()


    def visualize_tree(self):
        nodes = []
        lines = []
        node_id = 0
        node_ids = []
        def visit(node):
            if not node:
                return

            node_ids.append(node)
            node_id = len(node_ids)
            node.node_id = node_id

            nodes.append('n%s [label="%s:%s"]' % (node_id, node.values, node.hash))
            visit(node.left)
            visit(node.right)

            if node.left:
                lines.append("n%s -> n%s" % (node.node_id, node.left.node_id))
            elif node.right:
                null_id = "null%sL" % (node_id)
                lines.append("%s [shape=point]" % null_id)
                lines.append("n%s -> %s" % (node.node_id, null_id))

            if node.right:
                lines.append("n%s -> n%s" % (node.node_id, node.right.node_id))
            elif node.left:
                null_id = "null%sR" % (node_id)
                lines.append("%s [shape=point]" % null_id)
                lines.append("n%s -> %s" % (node.node_id, null_id))

            return nodes, lines

        visit(self)
        return nodes, lines

    def print_tree(self):
        nodes, lines = self.visualize_tree()

        ret = []
        ret.append( "digraph G {")
        ret.append(" graph[ordering=out];")
        for node in nodes:
            ret.append( " " + node + ";")

        for line in lines:
            ret.append( " " + line + ";")

        ret.append( "}")

        return ret

class ShardTree():
    def __init__(self, k=4):
        self.k = k
        self.server_tree = BinaryTree()

    def add_shard(self, server):
        for x in xrange(self.k):
            x *= x * 37
            serverid = hash("%s:%s:%s" % (x, server, x)) % modulo
            self.server_tree.add_value(server, serverid)

    def remove_shard(self, server):
        self.server_tree.remove_value(server)

    def get_shard(self, url):
        h = hash(url)
        s = self.server_tree.find_successor(h)
        return s.values[0]

if __name__ == "__main__":
    st = ShardTree()
    num_shards = 20
    for i in xrange(1, num_shards):
        st.add_shard(i)


    num_urls = 10000
    urls = []
    server_assignments = {}
    server_populations = defaultdict(int)
    for i in xrange(1, num_urls):
        url = "http://%s/URL" % i
        urls.append(url)

    for url in urls:
        s = st.get_shard(url)
        server_assignments[url] = s

    st.add_shard("a_new_shard")
    same = 0
    for url in urls:
        s = st.get_shard(url)
        if server_assignments[url] == s:
            same += 1

        server_populations[s] += 1
    print >> sys.stderr, "WITH NEW NODE", len(urls), same

    st.remove_shard("a_new_shard")
    same = 0
    server_populations = defaultdict(int)
    for url in urls:
        s = st.get_shard(url)
        if server_assignments[url] == s:
            same += 1

        server_populations[s] += 1

    print >> sys.stderr, "WITHOUT NEW NODE", len(urls), same
    print "\n".join(st.server_tree.print_tree())

    print >> sys.stderr, server_populations
    ser = st.server_tree.to_string()
    server_tree = BinaryTree.from_string(ser)
