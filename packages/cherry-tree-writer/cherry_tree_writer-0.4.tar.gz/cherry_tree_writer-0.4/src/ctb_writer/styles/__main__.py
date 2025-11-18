"""
List styles available
"""
from . import styles

print("Listing available styles:")
for name, color in styles.items():
    r, g, b = int(color[1:][0:2], 16), int(color[1:][2:4], 16), int(color[1:][4:],16)
    print(f"\x1b[38;2;{r};{g};{b}m{name}\x1b[0m", end=" | ")
print()
