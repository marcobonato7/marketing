import sys, os
root = sys.argv[1]
def sub(path, old, new, n=1):
    p = os.path.join(root, path); s = open(p).read()
    assert s.count(old) == n, (path, old[:70], s.count(old))
    open(p, 'w').write(s.replace(old, new))
J = 'assets/renn.js'
sub(J, '''        showToast("<span>Added: " + String(item.product_title || "item").replace(/</g, "&lt;") + "</span><a href=\\"" + R.cart + "\\">View cart</a>");''',
       '''        var nm = String(item.product_title || "item").replace(/</g, "&lt;");
        var img = item.image ? "<img src=\\"" + item.image + (item.image.indexOf("?") < 0 ? "?" : "&") + "width=120\\" alt=\\"\\">" : "";
        showToast(img + "<span class=\\"t-txt\\"><small>Added to your cart</small><b>" + nm + "</b></span><a href=\\"" + R.cart + "\\">View cart</a>");''')
C = 'assets/renn.css'
s = open(os.path.join(root, C)).read()
s += '''
/* ---------- add-to-cart pop-up: a wide card that fits the screen ---------- */
.toast{width:min(560px,calc(100vw - 24px));border-radius:20px;padding:12px 12px 12px 14px;gap:14px;justify-content:space-between;font-size:15px;line-height:1.3}
.toast img{width:52px;height:52px;flex:none;border-radius:12px;object-fit:contain;background:#fff}
.toast > span{flex:1 1 auto;min-width:0}
.toast .t-txt{display:grid;gap:3px}
.toast .t-txt small{font:400 11px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;opacity:.65}
.toast .t-txt b{font-weight:500;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.toast a{flex:none;padding:12px 18px;white-space:nowrap}
@media (max-width:620px){.toast{border-radius:18px;padding:10px 10px 10px 12px;gap:12px}.toast img{width:46px;height:46px}.toast a{padding:11px 14px;font-size:13.5px}}
'''
open(os.path.join(root, C), 'w').write(s)
print('patched')
