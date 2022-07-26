from util import powerset

EPSILON = 'ε'

class Node:
  def __init__(self, name, edges):
    self.name = name
    self.edges = {}
    self.unsafe_edges = {}
    for edge in edges:
      self.process_edge_string(edge)

  def process_edge_string(self, string):
    fail = Exception('Improperly formatted edge: \'' + string + '\'')
    parts = string.replace(' ', '').split('->')
    if len(parts) != 2:
      raise fail
    if parts[0] in self.unsafe_edges.keys():
      self.unsafe_edges[parts[0]].add(parts[1])
    else:
      self.unsafe_edges[parts[0]] = {parts[1]}


  def link_edges(self, node_references):
    for character, nodes in self.unsafe_edges.items():
      for node in nodes:
        if node_references[node] is None:
          raise Exception(
            'invalid edge destination for character \''
            + character +'\' in node \'' + self.name + '\''
          )
        else:
          if self.edges.get(character) is None:
            self.edges[character] = set()
          self.edges[character].add(node_references[node])

class FiniteStateAutomaton:
  def __init__(self, start, nodes, accept):
    self.nodes = {}
    self.accept = set()
    for node in nodes:
      self.nodes[node.name] = node
    for node in nodes:
      node.link_edges(self.nodes)
      if node.name in accept:
        self.accept.add(node)
    self.start = self.nodes[start]

  def accepts(self, string):
    return len(self.accept & self.navigate(self.start, string)) > 0

  def navigate(self, current, string):
    routes = {current} if len(string) == 0 else self.try_navigate(current, string[1:], string[0])
    routes.update(self.try_navigate(current, string, EPSILON))
    return routes

  def try_navigate(self, current, rest, character):
    neighbors = current.edges.get(character)

    destinations = set()
    if neighbors is not None:
      for neighbor in neighbors:
        destinations.update(self.navigate(neighbor, rest))
    return destinations

  def get_unreachable(self):
    edges_into = {}
    for node in self.nodes.values():
      edges_into[node] = set()
    for node in self.nodes.values():
      for neighbors in node.edges.values():
        for neighbor in neighbors:
          edges_into[neighbor].add(node)
    return list(filter(
      lambda current: current != self.start and len(edges_into[current]) == 0,
      self.nodes.values()
    ))

  def simplify(self):
    unreachable = self.get_unreachable()
    while len(unreachable) > 0:
      self.accept -= set(unreachable)
      [self.nodes.pop(node.name) for node in unreachable]
      unreachable = self.get_unreachable()

  def to_dfa(self):
    # get all possible combinations of states
    combinations = list(map(lambda element: frozenset(element), list(powerset(self.nodes.values()))))
    combination_indices = {}
    for index, combination in enumerate(combinations):
      combination_indices[combination] = index

    # assign names to nodes representing state combinations
    def compound_name(sub_nodes):
      return 'q' + str(combination_indices[frozenset(sub_nodes)])

    # generate new nodes and transitions
    new_nodes = []
    for combination in combinations:
      compound_edges = {}
      # compile the transitions within a state combination
      for node in combination:
        for character, to in node.edges.items():
          # exclude epsilon transitions
          if character == EPSILON: continue
          neighbors = self.navigate(node, character)
          if character in compound_edges:
            compound_edges[character].update(neighbors)
          else:
            compound_edges[character] = set(neighbors)
      # build new node from compiled states and transitions
      new_nodes.append(Node(compound_name(combination), list(map(
        lambda value: value + '->' + compound_name(compound_edges[value]),
        compound_edges.keys()
      ))))

    # a state in the DFA is an accept state if at least one of its substates was one
    accept = [compound_name(sub_nodes) for sub_nodes in combinations if self.accept & sub_nodes]

    dfa = FiniteStateAutomaton(compound_name(self.navigate(self.start, '')), new_nodes, accept)
    dfa.simplify()
    return dfa