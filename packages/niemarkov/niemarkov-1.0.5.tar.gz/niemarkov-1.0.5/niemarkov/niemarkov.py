#!/usr/bin/env python3
'''
NieMarkov: Niema's Python implementation of Markov chains
'''

# imports
from ast import literal_eval
from gzip import open as gopen
from pathlib import Path
from pickle import dump as pdump, load as pload
from random import randint

# useful constants
NIEMARKOV_VERSION = '1.0.5'
ALLOWED_STATE_TYPES = {int, str}
DEFAULT_BUFSIZE = 1048576 # 1 MB #8192 # 8 KB
MODEL_EXT = {'dict', 'pkl'}

def check_state_type(state_label):
    '''
    Helper function to check state type and throw an error if not allowed

    Args:
        state_label (str): The label of the state to check
    '''
    if type(state_label) not in ALLOWED_STATE_TYPES:
        raise TypeError("Invalid state type (%s). Must be one of: %s" % (type(state_label), ', '.join(str(t) for t in ALLOWED_STATE_TYPES)))

def open_file(p, mode='rt', buffering=DEFAULT_BUFSIZE):
    '''
    Open a file for reading/writing

    Args:
        p (Path): The path of the file to open, or `None` for `stdin`/`stdout`
        mode (str): The mode to open the file stream in
        buffering (int): The size of the file I/O buffer

    Returns:
        file: The opened file
    '''
    mode = mode.strip().lower()
    if isinstance(p, str):
        p = Path(p)
    if p is None:
        if 'r' in mode:
            from sys import stdin as f
        else:
            from sys import stdout as f
    elif p.suffix == '.gz':
        f = gopen(p, mode=mode)
    else:
        f = open(p, mode=mode)
    return f

def random_choice(options):
    '''
    Helper function to randomly pick from a collection of options

    Args:
        options (dict): The options to randomly pick from (keys = options, values = count weighting that option)

    Returns:
        object: A random element from `options`
    '''
    sum_options = sum(options.values())
    random_int = randint(1, sum_options)
    curr_total_count = 0
    for option, count in options.items():
        curr_total_count += count
        if random_int <= curr_total_count:
            return option

class MarkovChain:
    '''Class to represent Markov chains'''
    def __init__(self, order=1):
        '''
        Initialize a `MarkovChain` object

        Args:
            order (int): The order of this Markov chain
        '''
        if not isinstance(order, int) or order < 1:
            raise ValueError("`order` must be a positive integer")
        self.version = NIEMARKOV_VERSION  # NieMarkov version number
        self.order = order                # order of this Markov chain
        self.labels = list()              # labels of the states of this Markov chain
        self.label_to_state = dict()      # `label_to_state[label]` is the state (`int` from 0 to `num_states-1`) labeled by `label`
        self.transitions = dict()         # for an `order`-dimensional `tuple` of states `node`, `transitions[node]` is a `dict` where keys = outgoing nodes (state `tuple`s), and values = transition counts
        self.initial_node = dict()        # `initial_node[node]` is the number of times `node` is at the start of a path

    def __str__(self):
        '''
        Return a string summarizing this `MarkovChain`

        Returns:
            str: A string summarizing this `MarkovChain`
        '''
        return '<NieMarkov v%s: order=%d; states=%d>' % (self.version, self.order, len(self.labels))

    def __iter__(self):
        '''
        Iterate over the nodes (state `tuple`s) of this `order`-order `MarkovChain`

        Yields:
            tuple: The next node (state `tuple`)
        '''
        nodes = set()
        for node_src, outgoing_dict in self.transitions.items():
            nodes.add(node_src)
            for node_dst in outgoing_dict:
                nodes.add(node_dst)
        for node in nodes:
            yield node

    def __getitem__(self, key):
        '''
        Return the outgoing transitions of a given node (state `tuple`)

        Args:
            key (tuple): A node (state `tuple`)

        Returns:
            dict: The outgoing transmissions of `key`
        '''
        try:
            return self.transitions[key]
        except KeyError:
            return dict()

    def get_label(self, node, delim=' '):
        '''
        Return the label of an `order`-order node (state `tuple`) of this `MarkovChain`

        Args:
            node (tuple): The node (state `tuple`) whose label to get
            delim (str): The delimiter to use to separate individual entities of `node`

        Returns:
            str: The label of `node`
        '''
        if isinstance(node, tuple):
            return delim.join(str(self.labels[state]) for state in node)
        else:
            return self.labels[node] # if user provides a state instead of a node (state `tuple`)

    def dump(self, p, buffering=DEFAULT_BUFSIZE):
        '''
        Dump this `MarkovChain` to a file

        Args:
            p (Path): The path of the file where this `MarkovChain` should be dumped
            buffering (int): The size of the file I/O buffer
        '''
        if isinstance(p, str):
            p = Path(p)
        model = {'version':self.version, 'order':self.order, 'labels':self.labels, 'transitions':self.transitions, 'initial': self.initial_node}
        if p.suffix.lower() == '.pkl' or p.name.lower().endswith('.pkl.gz'):
            with open_file(p, mode='wb', buffering=buffering) as f:
                pdump(model, f)
        elif p.suffix.lower() == '.dict' or p.name.lower().endswith('.dict.gz'):
            with open_file(p, mode='wt', buffering=buffering) as f:
                f.write(str(model))
        else:
            raise ValueError("Invalid output NieMarkov model filename (%s). Valid extensions: %s" % (p, ', '.join(ext for ext in sorted(MODEL_EXT))))

    def load(p, buffering=DEFAULT_BUFSIZE):
        '''
        Load a `MarkovChain` from a file

        Args:
            p (Path): The path of the file from which to load a `MarkovChain`
            buffering (int): The size of the file I/O buffer

        Returns:
            MarkovChain: The loaded `MarkovChain`
        '''
        # load model from file
        if isinstance(p, str):
            p = Path(p)
        if p.suffix.lower() == '.pkl' or p.name.lower().endswith('.pkl.gz'):
            with open_file(p, mode='rb', buffering=buffering) as f:
                model = pload(f)
        elif p.suffix.lower() == '.dict' or p.name.lower().endswith('.dict.gz'):
            with open_file(p, mode='rt', buffering=buffering) as f:
                model = literal_eval(f.read())

        # check model for validity
        for k in ['order', 'labels', 'transitions', 'initial']:
            if k not in model:
                raise ValueError("Invalid model file (missing key '%s'): %s" % (k, p))

        # create and populate output `MarkovChain`
        mc = MarkovChain(order=model['order'])
        mc.version = model['version']
        mc.labels = model['labels']
        mc.label_to_state = {label:i for i, label in enumerate(mc.labels)}
        mc.transitions = model['transitions']
        mc.initial_node = model['initial']
        return mc

    def add_path(self, path):
        '''
        Add a path to this `MarkovChain`

        Args:
            path (list): A path of states
        '''
        # check `path` for validity
        if not isinstance(path, list):
            raise TypeError("`path` must be a list of state labels")
        if len(path) <= self.order:
            raise ValueError("Length of `path` (%d) must be > Markov chain order (%d)" % (len(path), self.order))


        # add new state labels
        for state_label in path:
            if state_label not in self.label_to_state:
                check_state_type(state_label)
                self.label_to_state[state_label] = len(self.labels)
                self.labels.append(state_label)

        # add path
        first_tup = tuple(self.label_to_state[path[j]] for j in range(self.order))
        if first_tup in self.initial_node:
            self.initial_node[first_tup] += 1
        else:
            self.initial_node[first_tup] = 1
        for i in range(len(path) - self.order):
            from_tup = tuple(self.label_to_state[path[j]] for j in range(i, i+self.order))
            to_tup = tuple(self.label_to_state[path[j]] for j in range(i+1, i+1+self.order))
            if from_tup in self.transitions:
                if to_tup in self.transitions[from_tup]:
                    self.transitions[from_tup][to_tup] += 1
                else:
                    self.transitions[from_tup][to_tup] = 1
            else:
                self.transitions[from_tup] = {to_tup: 1}

    def get_random_start(self):
        '''
        Return a random starting node (state `tuple`) in this `MarkovChain`

        Returns:
            tuple: A random starting node (state `tuple`) in this `MarkovChain`
        '''
        return random_choice(self.initial_node)

    def random_walk(self, start=None, include_start=False):
        '''
        Iterator that yields nodes (state `tuples`) in this `MarkovChain` according to a random walk

        Args:
            start (tuple): The starting node (state `tuple`), or `None` to randomly pick a starting node (state `tuple`)
            include_start (bool): `True` to include `start` as the first yielded node, otherwise `False`

        Yields:
            tuple: The next node (state `tuple`) in the random walk
        '''
        if start is None:
            curr_node = self.get_random_start()
        elif len(start) == self.order:
            curr_node = tuple(self.label_to_state[label] for label in start)
            if curr_node not in self.transitions:
                raise ValueError("No outgoing edges from start: %s" % start)
        else: # in the future, can do something fancy to handle this scenario, e.g. randomly pick an initial node (state `tuple`) ending with `start`
            raise ValueError("`start` length (%d) must be same as Markov model order (%d): %s" % (len(start), self.order, start))
        if include_start:
            yield curr_node
        while True:
            if curr_node not in self.transitions:
                break
            curr_node = random_choice(self.transitions[curr_node])
            yield curr_node

    def generate_path(self, start=None, max_len=float('inf')):
        '''
        Generate a random path in this `MarkovChain`

        Args:
            start (tuple): The starting node (state `tuple`), or `None` to randomly pick a starting node (state `tuple`)
            max_len (int): The maximum length of the random path to generate

        Returns:
            list: The randomly-generated path
        '''
        path = None
        for curr_node in self.random_walk(start=start, include_start=True):
            if path is None: # first node (state `tuple`), so add all states to path
                path = [self.labels[state] for state in curr_node]
            else:
                if len(path) >= max_len:
                    break
                path.append(self.labels[curr_node[-1]])
            if len(path) >= max_len:
                break
        if isinstance(max_len, int):
            path = path[:max_len]
        return path

    def to_dot(self):
        '''
        Get a representation of this `MarkovChain` in the Graphviz DOT format

        Returns:
            str: The DOT representation of this `MarkovChain`
        '''
        nodes = list(self)
        node_to_ind = {node:i for i, node in enumerate(nodes)}
        node_labels = [self.get_label(node) for node in nodes]
        nodes_str = '\n'.join('    %s [label="%s"];' % (node, node_label.strip().replace('"',"'")) for node, node_label in enumerate(node_labels))
        edges_str = '\n'.join('    %d -> %d [label="%s"];' % (node_to_ind[node_src], node_to_ind[node_dst], edge_count) for node_src in nodes for node_dst, edge_count in self[node_src].items())
        return 'digraph G {\n    // nodes\n%s\n\n    // edges\n%s\n}\n' % (nodes_str, edges_str)

    def to_cosmograph(self, delim='\t'):
        '''
        Get a representation of this `MarkovChain` in the Cosmograph (cosmograph.app) format

        Args:
            delim (str): The delimiter to use to separate columns

        Returns:
            str: The Cosmograph representation of this `MarkovChain`
        '''
        nodes = list(self)
        node_labels = [self.get_label(node).replace(delim,'') for node in nodes]
        node_to_ind = {node:i for i, node in enumerate(nodes)}
        edges_str = '\n'.join('%s%s%s%s%s' % (node_labels[node_to_ind[node_src]], delim, node_labels[node_to_ind[node_dst]], delim, edge_count) for node_src in nodes for node_dst, edge_count in self[node_src].items())
        return 'source%starget%svalue\n%s\n' % (delim, delim, edges_str)
