import matplotlib.pyplot as plt
import numpy as np

def plot_label(overuse_ratio):
    labels = ["A+++", "A++", "A+", "A", "B", "C", "D"]
    value_ranges = [5, 15, 30, 50, 80, 150, 300]  # Adjust the upper limit for each range
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(labels)))  # Colors from green to red

    fig, ax = plt.subplots(figsize=(10, 8))

    for i, (label, value, color) in enumerate(zip(labels, value_ranges, colors)):
        ax.barh(label, value, color=color, edgecolor='black')

    # Determine the appropriate range for the overuse ratio
    if overuse_ratio < 5:
        value_ratio = overuse_ratio
        ratio_label = f"<5"
        idx = 0
    elif overuse_ratio > 150:
        value_ratio = 150
        ratio_label = f">150"
        idx = len(labels) - 1
    else:
        value_ratio = overuse_ratio
        ratio_label = f'{overuse_ratio:.2f}'
        idx = np.digitize(overuse_ratio, value_ranges) - 1

    color_value = colors[idx]
    assigned_letter = labels[idx]
    ax.axvline(x=value_ratio, color=color_value, linewidth=3)
    ax.text(value_ratio + 1, len(labels) - idx - 1, ratio_label, va='center', ha='left', color=color_value, fontsize=12, fontweight='bold')

    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 300)  # Adjust the maximum limit to fit the ranges
    ax.invert_yaxis()
    plt.xlabel('Ratio')
    plt.ylabel('Resource Use Efficiency')
    plt.title('Resource Overuse Ratio Label')
    plt.tight_layout()
    return fig, ax, assigned_letter

if __name__ == "__main__":
    plt.show()
