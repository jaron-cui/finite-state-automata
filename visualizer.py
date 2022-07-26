import graphviz

class FsaVisualizer:
  def __init__(self, graph):
    self.graph = graph

  def visualize(self):
    f = graphviz.Digraph('finite_state_machine', filename='fsm.gv')
    f.attr(rankdir='LR', size='8,5')

    # render nodes
    for node in self.graph.nodes.values():
      f.attr('node', shape='doublecircle' if node in self.graph.accept else 'circle')
      f.node(node.name)

    # render edges
    f.node('INVISIBLE_START', label='', shape='none', height='0', width='0')
    f.edge('INVISIBLE_START', self.graph.start.name)
    for node in self.graph.nodes.values():
      paths = {}
      for character, destinations in node.edges.items():
        for destination in destinations:
          if paths.get(destination) is None:
            paths[destination] = character
          else:
            paths[destination] += ', ' + character
      for destination, label in paths.items():
        f.edge(node.name, destination.name, label=label)

    f.view()