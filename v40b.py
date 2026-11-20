import sys, os
root = sys.argv[1]
p = os.path.join(root, 'assets/renn.css'); s = open(p).read()
old = '''.collage5{display:grid;grid-template-columns:1.2fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:2px;background:#fff;aspect-ratio:1}
.collage5 img{width:100%;height:100%;object-fit:contain;background:#fff;min-height:0}
.collage5 .big{grid-row:1/3}
'''
new = '''.collage5{display:grid;grid-template-columns:1.3fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:2px;background:#fff}
.collage5 img{width:100%;height:100%;object-fit:cover;background:#fff;min-height:0;min-width:0}
.collage5 .big{grid-row:1/3;object-position:62% 50%}
.deal-img .tile{aspect-ratio:4/3}
.deal-img .tile.collage img{object-fit:cover}
'''
assert s.count(old) == 1; s = s.replace(old, new); open(p, 'w').write(s); print('patched')
