import sys, os
root = sys.argv[1]
for f in ['sections/renn-footer.liquid', 'sections/renn-film.liquid']:
    p = os.path.join(root, f); s = open(p).read()
    old = '"default": "Quiet steps. Real results."'
    assert s.count(old) == 1, f
    open(p, 'w').write(s.replace(old, '"default": "Less effort. More glow."'))
print('patched')
