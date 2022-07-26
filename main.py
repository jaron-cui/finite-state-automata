from fsa import FiniteStateAutomaton, Node
from visualizer import FsaVisualizer

M = FiniteStateAutomaton('q1', [
  Node('start', ['a->q1', 'ε->q2']),
  Node('', ['a->q1', 'b->q1'])
], ['q1']).to_dfa()
G = FsaVisualizer(M)
G.visualize()
print(M.accepts('')) # -> true
print(M.accepts('a')) # -> true
print(M.accepts('b')) # -> false
print(M.accepts('aaaab')) # -> false