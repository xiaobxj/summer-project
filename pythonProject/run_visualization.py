#!/usr/bin/env python3
"""
便捷的X-DATE可视化运行脚本
Run X-DATE Visualization Script
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Import and run visualization
from src.visualization.xdate_visualization import main

if __name__ == "__main__":
    main() 