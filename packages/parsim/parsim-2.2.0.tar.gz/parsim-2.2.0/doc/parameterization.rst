Parametrization of files and scripts
====================================

Parsim uses the Python library pyexpander to process parameterized text files in a model template.
You must add the extension ``.macro`` to the name of all files containing parameters or macros;
the extension is removed when a case is created and the file is processed for macro expansion.

Each template file is processed, "expanded", individually. The parsing of a file takes place in a Python session, where
all the model parameters exist as variables in the global namespace.
Template files usually consist mostly of pure text, which is simply echoed as-is to the corresponding case file.

The **pyexpander** library allows you to do very advanced operations in your input files,
for example inserting Python code blocks for calculating complex constructs, working with loops and conditionals,
include other files, etc. Some of these possibilities are explained below; see the pyexpander documentation
for additional details. Note that some of the text below is copied from the official pyexpander documentation.

The meaning of the dollar sign
------------------------------

Almost all elements of the pyexpander language start with a dollar "$" sign. If a dollar
is preceded by a backslash "\\" it is escaped. The "\\$" is then replaced with
a simple dollar character "$" and the rules described further down do not
apply.

Here is an example: ::

  an escaped dollar: \$

This would produce this output: ::

  an escaped dollar: $

Parameter substitution
----------------------

The syntax for parameter substitution is a valid parameter name enclosed in ``$()``.
For example, to introduce a parameter ``DENSITY`` in an input file, you would replace all
occurencies of the nominal value by the string ``$(DENSITY)``.
What is inside the brackets must be a valid Python expression.
Note that a python expression, in opposition to a python statement,
always has a value. This value is converted to a string and this string is
inserted in the text in place of the substitution command.

The use of python expressions for parameter substitutions allows you to
do more advanced substitutions. For example, you could compute and
insert the mass, by multiplying parameters for density and volume: ``$(DENSITY*VOLUME)``.

Comments
--------

A comment is started by a sequence "$#" where the dollar sign is not preceded
by a backslash (see above). All characters until and including the end of line
character(s) are ignored. Here is an example::

  This is ordinary text, $# from here it is a comment
  here the text continues.

Commands
--------

If the dollar sign, which is not preceded by a backslash, is followed by a
letter or an underline "_" and one or more alphanumeric characters, including
the underline "_", it is interpreted to be an expander command.

The *name* of the command consists of all alphanumeric characters including "_"
that follow. In order to be able to embed commands into a sequence of letters,
as a variant of this, the *name* may be enclosed in curly brackets. This
variant is only allowed for commands that do not expect parameters.

If the command expects parameters, an opening round bracket "(" must
immediately (without spaces) follow the characters of the command name. The
parameters end with a closing round bracket ")".

Here are some examples::

  this is not a command due to escaping rules: \$mycommand
  a command: $begin
  a command within a sequence of letters abc${begin}def
  a command with parameters: $for(x in range(0,3))

Note that in the last line, since the parameter of the "for" command must be a
valid python expression, all opening brackets in that expression must match a
closing bracket. By this rule pyexpander is able to find the closing bracket
that belongs to the opening bracket of the parameter list.

Executing python statements and code blocks
-------------------------------------------

A statement may be any valid python code. Statements usually do not return
values. All expressions are statements, but not all statements are
expressions.

In order to execute python statements, there is the "py" command.
"py" is an abbreviation of python. This command expects that valid python code
follows enclosed in brackets. Note that the closing bracket for "py" *must not*
be in the same line with a python comment, since a python comment would include
the bracket and all characters until the end of the line, leading to a
pyexpander parser error.

The "py" command leads to the execution of the python
code but produces no output. It is usually used to define variables, but it can
also be used to execute python code of more complexity. Here are some
examples::

  Here we define the variable "x" to be 1: $py(x=1)
  Here we define two variables at a time: $py(x=1;y=2)
  Here we define a function, note that we have to keep
  the indentation that python requires intact:
  $py(
  def multiply(x,y):
      return x*y
      # here is a python comment
      # note that the closing bracket below
      # *MUST NOT* be in such a comment line
     )

.. warning::

    The syntax for the pyexpander library can in principle be used to *redefine* the value of a model
    parameter inside a parameterized text files. **NEVER DO THIS**, as it breaks the link between
    the values you define when you created the case and the actual values in your input files!

Importing modules in code blocks
................................

You can import modules inside code blocks. Any imported modules and packages will then be
available for use also in substitutions and other code blocks later in the same template file.

In order to allow import of your own modules, parsim prepends some additional directories
to the Python search path (PYTHONPATH):

* ``bin`` subdirectory of the project directory,
* the template directory,
* the ``bin`` subdirectory of the template directory.

Working with files inside code blocks
.....................................

Before a template file is processed, the current directory is set to the corresponding destination directory
in the case. This makes it possible to write files during template processing, and have these available in the
case directory. This can be very useful, for example when debugging or generating data files for post-processing
and reporting.

See the following example, where
we have used the standard ``math`` module and ``matplotlib`` to generate a plot to illustrate the effect
of the relevant case parameters, while processing an inputfile for a solver. ::

    ghfgf
    fghfghf
    fgh
    fg
    fghf
    g

Line continuation
-----------------

Since the end of line character is never part of a command, commands placed on
a single line would produce an empty line in the output. Since this is
sometimes not wanted, the generation of an empty line can be suppressed by
ending the line with a single backslash "\\". Here is an example::

  $py(x=1;y=2)\
  The value of x is $(x), the value of y is $(y).
  Note that no leading empty line is generated in this example.

Conditionals
------------

A conditional part consists at least of an "if" and an "endif" command. Between
these two there may be an arbitrary number of "elif" commands. Before "endif"
and after the last "elif" (if present) there may be an "else" command. "if" and
"elif" are followed by a condition expression, enclosed in round brackets.
"else" and "endif" do not have parameters. If the condition after "if" is true,
this part is evaluated. If it is false, the next "elif" part is tested. If it
is true, this part is evaluated, if not, the next "elif" part is tested and so
on. If no matching condition was found, the "else" part is evaluated.

All of this is oriented on the python language which also has "if","elif" and "else".
"endif" has no counterpart in python since there the indentation shows where
the block ends.

Here is an example::

  We set x to 1; $py(x=1)
  $if(x>2)
  x is bigger than 2
  $elif(x>1)
  x is bigger than 1
  $elif(x==1)
  x is equal to 1
  $else
  x is smaller than 1
  $endif
  here is a classical if-else-endif:
  $if(x>0)
  x is bigger than 0
  $else
  x is not bigger than 0
  $endif
  here is a simple if-endif:
  $if(x==0)
  x is zero
  $endif

While loops
-----------

While loops are used to generate text that contains almost identical
repetitions of text fragments. The loop continues while the given loop
condition is true. A while loop starts with a "while" command followed by a
boolean expression enclosed in brackets. The end of the loop is marked by a
"endwhile" statement.

Here is an example::

  $py(a=3)
  $while(a>0)
  a is now: $(a)
  $py(a-=1)
  $endwhile

In this example the loop runs 3 times with values of a ranging from 3 to 1.

The command "while_begin" combines a while loop with a scope; see the pyexpander documentation.

For loops
---------

For loops are a powerful tool to generate text that contains almost identical
repetitions of text fragments. A "for" command expects a parameter that is a
python expression in the form "variable(s) in iterable". For each run the
variable is set to another value from the iterable and the following text is
evaluated until "endfor" is found. At "endfor", pyexpander jumps back to the
"for" statement and assigns the next value to the variable.

Here is an example::

  $for(x in range(0,5))
  x is now: $(x)
  $endfor

The range function in python generates a list of integers starting with 0 and
ending with 4 in this example.

You can also have more than one loop variable::

  $for( (x,y) in [(x,x*x) for x in range(0,3)])
  x:$(x) y:$(y)
  $endfor

or you can iterate over keys and values of a python dictionary::

  $py(d={"A":1, "B":2, "C":3})
  $for( (k,v) in d.items())
  key: $(k) value: $(v)
  $endfor

The command "for_begin" combines a for loop with a scope; see the pyexpander documentation.

Include files
-------------

The "include" command is used to include a file at the current position. It
must be followed by a string expression enclosed in brackets. The given file is
then interpreted until the end of the file is reached, then the interpretation
of the text continues after the "include" command in the original text.

Unless the file is given with an absolute path, it will be looked for first
in the current directory of the template (same location as the template file
being processed), then in the root of the template directory.

Here is an example::

  $include("additional_defines.inc")

The command "include_begin" combines an include with a scope. It is equivalent
to the case when the include file starts with a "begin" command and ends with
an "end" command. See the pyexpander documentation for a discussion on scopes.

