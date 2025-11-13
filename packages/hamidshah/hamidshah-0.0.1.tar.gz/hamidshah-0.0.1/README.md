# Count in List 🧮

A simple Python function that counts how many times a given word appears in a list using the `collections.Counter` class.

## Example

```python
from collections import Counter

def count_in_list(l, word):
    c = Counter(l)
    return c[word]

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
print(count_in_list(words, "apple"))  # Output: 3
