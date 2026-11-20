import sys, os
root = sys.argv[1]
def sub(path, old, new, n=1):
    p = os.path.join(root, path); s = open(p).read()
    assert s.count(old) == n, (path, old[:70], s.count(old))
    open(p, 'w').write(s.replace(old, new))
C = 'assets/renn.css'
sub(C, '''html.has-bar .hdr{top:var(--barh)}''', '''html.has-bar .hdr{top:var(--barh)}
/* with the promotion bar on, the film starts below it, so the logo, chapter label and cards keep their spacing */
html.has-bar .stage{top:var(--barh);height:calc(100vh - var(--barh));height:calc(100svh - var(--barh))}
html.has-bar .gallery{top:calc(96px + var(--barh))}
@media (max-width:820px){html.has-bar .chapter{top:84px}html.has-bar .loader{top:80px}}''')
J = 'assets/renn.js'
sub(J, '''        b.parentNode.hidden = true; document.documentElement.classList.remove("has-bar");''',
       '''        b.parentNode.hidden = true; document.documentElement.classList.remove("has-bar");
        if (window.RENN_RELAYOUT) window.RENN_RELAYOUT();''')
sub(J, '''    lastW = innerWidth; layout(); if (useSeq) size(); drawnF = -1; onScroll();
  });''', '''    lastW = innerWidth; layout(); if (useSeq) size(); drawnF = -1; onScroll();
  });
  window.RENN_RELAYOUT = function () { layout(); if (useSeq) size(); drawnF = -1; onScroll(); };   /* the promotion bar was closed */''')
print('patched')
