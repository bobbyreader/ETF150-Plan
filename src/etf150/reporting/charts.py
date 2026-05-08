from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from etf150.models import AllocationSlice


def configure_fonts() -> None:
    """Configure a CJK-capable font when available."""
    preferred_fonts = [
        "PingFang SC",
        "Hiragino Sans GB",
        "STHeiti",
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
    ]
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    for font_name in preferred_fonts:
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name, *plt.rcParams.get("font.sans-serif", [])]
            plt.rcParams["axes.unicode_minus"] = False
            return


def save_allocation_chart(slices: list[AllocationSlice], output_path: Path) -> Path:
    """Save an allocation pie chart."""
    configure_fonts()
    labels = [item.name for item in slices]
    sizes = [item.weight for item in slices]

    figure, axis = plt.subplots(figsize=(6, 6))
    axis.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    axis.axis("equal")
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)
    return output_path
