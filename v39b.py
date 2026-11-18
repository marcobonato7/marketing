import sys, os
root = sys.argv[1]
def rd(p): return open(os.path.join(root, p)).read()
def wr(p, s): open(os.path.join(root, p), 'w').write(s)
def sub(path, old, new, n=1):
    s = rd(path)
    assert s.count(old) == n, (path, old[:70], s.count(old))
    wr(path, s.replace(old, new))
S = 'sections/renn-shop.liquid'
sub(S, "{% render 'renn-tile', product: blank, fallback: fb_imgs[forloop.index0], fallback_title: n %}",
       "{% render 'renn-tile', fallback: fb_imgs[forloop.index0], fallback_title: n %}")
sub(S, "{% render 'renn-buy', product: blank, label: 'Shop Now', fallback_price: fb_prices[forloop.index0] %}",
       "{% render 'renn-buy', label: 'Shop Now', fallback_price: fb_prices[forloop.index0] %}")
J = 'assets/renn.js'
sub(J, '''      if (step === STEP) break;
    }
    var next = 0, active = 0;''', '''      if (step === STEP) break;
    }
    NEED = order.length;                                              /* every frame this device will load */
    var next = 0, active = 0;''')
print('patched')
