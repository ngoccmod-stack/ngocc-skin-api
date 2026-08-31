import os as c, sys as d
e = c.path.dirname(c.path.abspath(__file__))
f = c.path.dirname(e)
h = [c.path.join(f, 'lib'), f, c.path.dirname(f), c.getcwd()]
for b in h:
    if b and c.path.isdir(b):
        if c.path.isdir(c.path.join(b, 'UnityPy')) or c.path.isfile(c.path.join(b, 'Protect.py')):
            if b not in d.path:
                d.path.insert(0, b)
try:
    import UnityPy
except ImportError as a:
    raise SystemExit("\n[X] Khong thay thu muc 'UnityPy' (ban fork AOV).\n    Chep 'UnityPy/' va 'Protect.py' vao thu muc lib/ cua tool.\n    -> %s\n" % a)
try:
    import Protect as g
except ImportError as a:
    raise SystemExit("\n[X] Khong thay 'Protect.py' (chua key AES/SM4 cua AOV).\n    Chep 'Protect.py' vao thu muc lib/ cua tool.\n    -> %s\n" % a)
decrypt_bundle = g.decrypt_bundle
encrypt_bundle = g.encrypt_bundle
