Advanced installation options
=============================

See Section :ref:`installation` for standard installation instructions.

Repository installation
-----------------------

The `code base for Parsim <https://gitlab.com/olwi/psm>`_ is hosted at `gitlab.com <gitlab.com>`_.
First clone the git repository in an appropriate location: ::

    git clone https://olwi@gitlab.com/olwi/psm.git psm

Even if you use ``conda`` as your package manager, it is easiest to use ``pip`` for installing an editable
development version of parsim. However, do this in a special conda enviroment! Once you have used ``pip`` in the
conda installation, it may be difficult for conda to update other packages without dependency conflicts.

In your development python environment, enter the working copy of the source repository and
use ``pip`` to install parsim in editable development mode: ::

    cd psm
    pip install -e .


Updating an existing installation
-------------------------------------

If you upgrade and existing installation with ``pip install --upgrade``, it is
recommended to do it without upgrading dependencies, unless it is required.
This is to avoid triggering an upgrade of NumPy and SciPy, which could break your installation.

Do the upgrade in two steps. First upgrade parsim, but not dependencies: ::

    pip install --upgrade --no-deps parsim

Then update whatever requirements are not already fulfilled: ::

    pip install parsim

The two-step process for upgrading a repository installation is analogous.

