.. _minimal nestedtext:

******************
Minimal NestedText
******************

*Minimal NestedText* is a subset of *NestedText* that foregoes some of the
complications of *NestedText*.  It sacrifices the completeness of *NestedText*
for an even simpler data file format that is still appropriate for
a surprisingly wide variety of applications, such as most configuration files.
The simplicity of *Minimal NestedText* makes it very easy to create readers and
writers.  Indeed, writing such functions is good programming exercise for people
new to recursion.

*Minimal NestedText* is *NestedText* without support for multi-line keys and
inline dictionaries and lists.

If you choose to create a *Minimal NestedText* reader or writer it is important
to code it in such a way as to discourage the creation *Minimal NestedText*
documents that are invalid *NestedText*.  Thus, your implementation should
disallow keys that start with ``: ``, ``[`` or ``{``.  Also, please clearly
indicate that is only supports *Minimal NestedText* to avoid any confusion.

Many of the examples given in this document conform to the *Minimal NestedText*
subset.  For convenience, here is another:

.. code-block:: nestedtext

    name: No-Soak Instant Pot Chili

    description:
        > Chili with meat and beans.
        >
        > Takes a little over an hour from start to finish while starting with
        > dried beans that have not be pre-soaked.

    source: https://thefreerangelife.com/instant-pot-chili

    ingredients:
        ground beef: 1-2 pounds
        onion: 1
        garlic: 3-4 cloves
        dry red kidney beans: 1 16-oz bag
        broth: 4 cups
        chili powder: 3 tablespoon
        dried oregano: 1-2 teaspoon
        cumin: 1 teaspoon (optional)
        dice tomatoes: 6 cups (2 large cans or grow your own)
        water: 2-3 cups
        salt and pepper: to taste

    directions:
      -
        > Place the 4 cups of broth and the dry kidney beans into the pot of your
        > Instant Pot
      -
        > Add 2 T of chili powder and salt and pepper
      -
        > Place the lid on your Instant Pot and press the bean setting. The timer
        > should read 30 minutes. Allow it to come to pressure and cook.
      -
        > While the beans are cooking, saute beef with onion and garlic.
      -
        > When the timer beeps, do a quick release and open up the pot
      -
        > Add the meat, tomatoes, water, oregano, cumin, and the additional 1T of
        > chili powder and stir well.
      -
        > At this point your pot should be quite full. Close up the Instant Pot
        > again and hit the chili/beans button once more. Allow it to come to
        > pressure and cook.
      -
        > Do a quick release when the chili has finished cooking.

    comments:
        > This instant pot chili assumes dried beans.
        >
        > It takes TWO 30 minute cycles.
        > One with just the beans and one with all the ingredients together.
        >
        > If you are not using dried beans, you can skip the first cycle and
        > simply add all of the ingredients to the pot and cook for 30 minutes
        > at high pressure.

*Minimal NestedText* is powerful enough to satisfy most needs.  It is only
necessary to use the extended capabilities of *NestedText* if you have keys that
start with reserved characters or contain newlines or if your document contains
lots of short lists or dictionaries.  In the later situation, being constrained
to use *Minimal NestedText* might make entry tedious.

Here is another example of *Minimal NestedText* that shows off a particular
strength of *NestedText*, its ability to hold code fragments without the need
for quoting or escaping.  It holds some `Parametrize From File
<https://parametrize-from-file.readthedocs.io>`_ test cases for `pytest
<https://docs.pytest.org>`_:

.. code-block:: nestedtext

    test_meta_view:
      -
        id: base
        obj:
          > class DummyConfig(Config):
          >     def load(self):
          >         yield DictLayer({"x": 1}, location="/path/to/file")
          >
          > class DummyObj:
          >     __config__ = [DummyConfig]
          >     meta = byoc.meta_view()
          >     x = byoc.param()
          >
          > obj = DummyObj()
          > obj.x
        expected:
          x:
            type: LayerMeta
            location: /path/to/file
      -
        id: never-accessed
        obj:
          > class DummyObj:
          >     meta = byoc.meta_view()
          >     x = byoc.param()
        expected:
          x: NeverAccessedMeta
