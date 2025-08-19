***********************
The Zen of *NestedText*
***********************

*NestedText* aspires to be a simple dumb receptacle that holds peoples' 
structured data and does so in a way that allows people to easily interact with 
that data.

The desire to be simple is an attempt to minimize the effort required to learn 
and use the language.  Ideally, people can understand it by looking at a few 
examples. And ideally, they can use it without needing to remember any arcane 
rules or relying on any knowledge that programmers accumulate through years of 
experience.  One source of simplicity is consistency.  As such, *NestedText* 
uses a small number of rules that it applies with few exceptions.

The desire to be dumb means that *NestedText* does not transform the data in any 
meaningful way to avoid creating unpleasant surprises.  Specifically, when you 
enter *NestedText* you are specifying a sequence of characters.  Beyond 
extracting the structure of the data, *NestedText* does not interpret what you 
mean by a particular sequence of characters.  All leaf values are left as 
strings.  Any interpretation or conversion of the data must be explicitly done 
by you after the data is read.  After all, you understand what the data is 
supposed to mean, so you are in the best position to interpret it.  There are 
many powerful tools available to help with :doc:`this exact task <schemas>`, and 
they turn what may initially seem like a burden into a substantial advantage.

The specifics of *NestedText*
-----------------------------

When people make a list they often start out by numbering the items.  For 
example, if you are making a list of toiletries to take on a trip you might 
create the following list::

    1. tooth brush
    2. tooth paste
    3. floss
    4. shaver

This is an enumerated list.

But as you start editing the list, you may find that you are spending too much 
time renumbering the items, and so you often convert to the simpler system of 
identifying each item with a bullet, such as::

    - tooth brush
    - tooth paste
    - floss
    - shaver

This is also an enumerated list, but here the enumeration is implicit.

This is the form used by *NestedText* to identify the items in a list.  It is 
a very natural form that people tend to use instinctively.

Then if the list grows and you want to add sections.  The natural approach is 
the following::

    toiletries:
        - tooth brush
        - tooth paste
        - floss
        - shaver

This type of list, where a key is specified rather than a bullet, is a keyed 
list.  Again, this is the form used by *NestedText*.

Notice it was natural to nest our first list into this new list by indenting it.

Things become a bit more complicated when list item values grow to be more than 
one line long.  In this case there are two common approaches.  This first is to 
simply continue on the next line while maintaining the indent.  For example::

    toiletries:
        - tooth brush
          the green one
        - tooth paste
          a new tube
        - floss
          mint flavor
        - shaver
          the electric one

A second approach is to place all the text on a separate line from the bullet, 
as in::

    toiletries:
        -
          tooth brush
          the green one
        -
          tooth paste
          a new tube
        -
          floss
          mint flavor please, its delightful
        -
          shaver
          the electric one


If one had to choose one format to use every time, one would generally choose 
the second because it is more natural for keyed lists.

However, there are more issues.  Imagine that the multi-line text is indented.  
How would that be indicated?  Or perhaps there are leading or trailing blank 
lines, how would those be distinguished from the empty space used to make our 
list more readable.  To resolve these issues, *NestedText* deviates from normal 
convention by asking you to draw the left border of the text.  For example::

    Step 3: Pressure Cook
        |     Close the lid and seal the vent. Press the “pressure cook” button
        | and set the time to 10 minutes. After this, allow natural pressure
        | release for 5 minutes, then manually release the remaining pressure.

Doing so makes any indention and blank lines completely unambiguous.  As such, 
it is the approach that *NestedText* takes.  However it does not use the ‘|’ 
character to indicate the border.  It was found that with most text editors the 
‘>’ character works better because the editor treats it as a continuation 
character, meaning once the multiline text was started, typing a new line 
automatically brings the next ‘>’ character with an additional space of indent.  
This allows you to type multiple lines without consciously entering these 
continuation characters, making the process very efficient.  Thus, with 
*NestedText* you would enter::

    Step 3: Pressure Cook
        >     Close the lid and seal the vent. Press the “pressure cook” button
        > and set the time to 10 minutes. After this, allow natural pressure
        > release for 5 minutes, then manually release the remaining pressure.

An there you have it.  This, plus a few rules to eliminate any remaining 
ambiguities and to handle some unusual special cases and you have *NestedText*.
