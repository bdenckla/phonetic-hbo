# phonetic-hbo legacy URL host

This repository preserves old published URLs with generated redirects. The maintained
products and generators now belong to MAM-basics:

- [Phonetic MAM](https://bdenckla.github.io/MAM-basics/phonetic-mam/index.html)
- [Yeivin ITM excerpts](https://bdenckla.github.io/MAM-basics/yeivin-itm/yeivin_itm.html)

Every frozen HTML path is declared in
[MAM-basics' redirect manifest](https://github.com/bdenckla/MAM-basics/blob/main/in/phonetic_hbo_redirect_pages.json).
Generate and check those stubs through MAM-basics' `py/main_redirect_stubs.py`;
do not hand-edit them here. The old `tnkh/` URLs select Sephardic pronunciation;
the old `tnkh-ashkenaz/` URLs select Ashkenazic pronunciation in the same maintained
`tnkh/` tree. JavaScript preserves unrelated query parameters and fragments, and
the legacy path's pronunciation overrides an incoming conflicting value.

Without JavaScript, a known page automatically refreshes to its fixed target:
the declared pronunciation survives, while incoming query parameters and fragments
are lost. Unknown paths receive GitHub Pages' HTTP 404 response and the fixed
Phonetic MAM homepage fallback. With JavaScript that fallback preserves unrelated
query parameters and the fragment and fixes Sephardic pronunciation. Without
JavaScript, the reader must click its fallback link.

The existing stylesheet, Taamey D font and five small Jacobson image crops remain
at their old asset URLs byte for byte. Their separate terms are in
[`LICENSE.md`](LICENSE.md); an HTML redirect cannot replace a static asset URL.

The historical issues and citations stay in this repository's tracker. File new
public-product issues in [MAM-basics](https://github.com/bdenckla/MAM-basics/issues)
and new private-source issues in
[MAM-private](https://github.com/bdenckla/MAM-private/issues). This repository remains
unarchived so its redirects, history and historical issue tracker remain available.

Private source work remains in MAM-private's `al-hatorah/` tree, formerly the
[al-hatorah](https://github.com/bdenckla/al-hatorah) repository. The related
`masorah-books/` tree also remains in MAM-private, with sources and research tooling
for the ITM adaptation. The maintained public adaptation is in MAM-basics.
