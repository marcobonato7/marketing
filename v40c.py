import sys, os
root = sys.argv[1]
p = os.path.join(root, 'snippets/renn-promo-bar.liquid'); s = open(p).read()
old = '<span class="sep" aria-hidden="true"></span>Code <button'
assert s.count(old) == 2; s = s.replace(old, '<span class="sep" aria-hidden="true"></span><span class="lbl">Code</span> <button'); open(p, 'w').write(s)
p = os.path.join(root, 'assets/renn.css'); s = open(p).read()
old = '@media (max-width:640px){.pbar{font-size:12.5px;padding:0 40px 0 14px;justify-content:flex-start}.pbar .hide-s{display:none}}'
new = '''@media (max-width:640px){.pbar{font-size:12.5px;padding:0 40px 0 14px;justify-content:flex-start}.pbar .hide-s,.pbar .lbl{display:none}
  .pbar p{width:100%;min-width:0}.pbar b{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis}.pbar .code{flex:none;padding:5px 7px}}'''
assert s.count(old) == 1; s = s.replace(old, new); open(p, 'w').write(s); print('patched')
