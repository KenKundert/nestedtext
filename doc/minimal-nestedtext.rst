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
disallow keys that start with ``:␣``, ``[`` or ``{``.
