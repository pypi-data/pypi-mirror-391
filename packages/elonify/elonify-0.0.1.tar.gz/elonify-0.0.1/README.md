# elonify 🚀

The one-liner web toolkit that auto-thinks like Elon.

```python
from elonify import get

r = get("https://github.com/abrlake/elonify")
print(r.json["public_repos"])
✅ Auto-detects JSON / HTML
✅ Simple .get() API
✅ .json, .html, .text, .find() — all built in

---

Once this is in your folder, you can package it with:
```bash
python setup.py sdist bdist_wheel
twine upload dist/*

