import networkx as nx

def get_node_of_address(graph: nx.Graph, address: str):
    """
    Get the node of a given address in the graph.

    Parameters
    ----------
    graph : networkx.Graph
        The networkx graph to search in
    address : str
        The address string to search for 

    Returns
    -------
    int or None
        The node ID if found, None otherwise
    """
    for u, v, data in graph.edges(data=True):
        if address.lower() in data.get('name', '').lower():
            return u
    return None