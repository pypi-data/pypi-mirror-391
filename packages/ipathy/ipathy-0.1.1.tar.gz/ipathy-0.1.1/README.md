# Pathy 🧩  
**The path fixer your OS forgot.**

Cross-platform path normalizer for Python.  
Because Windows slashes are chaos 💀.

```python
from pathy import pathy

print(pathy("C:\\Users\\Me\\Desktop\\..\\file.txt"))
# ➜ /Users/Me/file.txt
