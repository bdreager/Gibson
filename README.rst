Gibson
======

What
~~~~

Crazy terminal vomit. You too can look like you're hacking the gibson.


Requires
~~~~~~~~

ncurses


Controls
~~~~~~~~

+------------------------------------+--------------------------------------+
| Keys                               | Actions                              |
+====================================+======================================+
| ``q`` or ``Q`` or ``Esc``          | quit                                 |
+------------------------------------+--------------------------------------+
| ``p`` or ``P``                     | pause                                |
+------------------------------------+--------------------------------------+
| ``-`` or ``_``                     | decrease delay (5ms) between updates |
+------------------------------------+--------------------------------------+
| ``=`` or ``+``                     | increase delay (5ms) between updates |
+------------------------------------+--------------------------------------+

Command-line options
~~~~~~~~~~~~~~~~~~~~

+------------------------------------+--------------------------------------+
| Options                            | Descriptions                         |
+====================================+======================================+
| ``-h`` or ``--help``               | show help message                    |
+------------------------------------+--------------------------------------+
| ``--version``                      | show current version                 |
+------------------------------------+--------------------------------------+

Support
~~~~~~~

-  [x] Works on Linux completely

-  [x] Works on OSX completely

-  [ ] Windows not supported

Caveats
~~~~~~~

This is a stupid, gaudy script and might run very poorly.
The output is dependent on the size of the terminal window. If it runs poorly, shrink the window until it runs sort-of-okay

For terminal windows under a certain size, the script will just crash. This will be fixed in the future.
