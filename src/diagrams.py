import matplotlib.pyplot as plt
import networkx as nx
import re


def get_node_size(value):
    """Determine the node size based on the value."""
    return value * 500  # Adjust the multiplier to make sizes more perceptible


def get_node_color(value):
    """Determine the node color based on the value."""
    if value < 1:
        return 'lightblue'
    elif value < 5:
        return 'skyblue'
    elif value < 10:
        return 'dodgerblue'
    else:
        return 'darkblue'


def extract_value(label):
    """Extract the numerical value from a label string."""
    match = re.search(r'(\d+\.\d+)', label)
    if match:
        return float(match.group(1))
    else:
        return 1.0  # Default value in case of error


def create_hierarchical_layout(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    Generate a hierarchical layout for a directed graph (DAG) without using Graphviz.

    Parameters:
    - G: Graph (NetworkX DiGraph)
    - root: Root node for hierarchical layout
    - width: Horizontal space allotted for the layout
    - vert_gap: Gap between layers vertically
    - vert_loc: Initial vertical location of the root node
    - xcenter: Center of the layout horizontally

    Returns:
    - pos: Dictionary of node positions
    """
    if not nx.is_tree(G):
        raise TypeError("The graph must be a tree")

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        """Recursively generate positions for each node."""
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)

        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph):
            children = [child for child in children if child != parent]

        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap,
                                     xcenter=nextx, pos=pos, parent=root, parsed=parsed)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def create_diagram(et0, etc, nhn, nhn_adjusted, water_need, dn_turn, dn_hour, db, irrigation_turn, liters_per_dripper):
    """Create a relationship diagram between different parameters."""
    G = nx.DiGraph()

    # Add nodes and their labels
    nodes = {
        "ET0": f"ET0 - {et0:.2f} mm/day",
        "ETc": f"ETc - {etc:.2f} mm/day",
        "NHn": f"NHn - {nhn:.2f} mm/day",
        "NHn adjusted": f"NHn adjusted - {nhn_adjusted:.2f} mm/day",
        "Water Need": f"Water Need for a turn of {irrigation_turn} days - {water_need:.2f} mm/{irrigation_turn} days",
        "Net Water Demand (DN) per turn": f"Net Water Demand (DN) adjusted per irrigation turn - {dn_turn:.2f} l/(m2*{irrigation_turn} days)",
        "Net Water Demand (DN) per hour": f"Net Water Demand (DN) adjusted per irrigation hours - {dn_hour:.2f} l/(h*m2)",
        "Gross Water Demand (DB)": f"Gross Water Demand (DB) during 8.0 hours of irrigation - {db:.2f} l/(h*m2)",
        "Ideal liters per dripper": f"Ideal liters per dripper - {liters_per_dripper:.2f} l/h"
    }

    for key, label in nodes.items():
        G.add_node(key, label=label)

    # Add edges to represent relationships
    edges = [
        ("ET0", "ETc"),
        ("ETc", "NHn"),
        ("NHn", "NHn adjusted"),
        ("NHn adjusted", "Water Need"),
        ("Water Need", "Net Water Demand (DN) per turn"),
        ("Net Water Demand (DN) per turn", "Net Water Demand (DN) per hour"),
        ("Net Water Demand (DN) per hour", "Gross Water Demand (DB)"),
        ("Gross Water Demand (DB)", "Ideal liters per dripper")
    ]

    G.add_edges_from(edges)

    # Configure the hierarchical layout from top to bottom
    pos = create_hierarchical_layout(G, root="ET0")

    # Extract values to determine sizes and colors
    node_sizes = [get_node_size(extract_value(label)) for label in nodes.values()]
    node_colors = [get_node_color(extract_value(label)) for label in nodes.values()]

    labels = nx.get_node_attributes(G, 'label')
    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=node_sizes, node_color=node_colors, node_shape="o",
            alpha=0.75, linewidths=1, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): '' for u, v in G.edges()}, font_color='black', ax=ax)

    plt.title('Consumption Diagram')
    plt.tight_layout()
    return fig, ax
