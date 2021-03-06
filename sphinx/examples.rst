CLI examples
============

The first argument  in a TSValid command is always the TSV file.
Without any arguments, all TSValid checks will be run.


.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv

The (shortened) output looks like:

.. code-block:: bash

    tests/data/test_all_wrong.tsv:1:0: E1: Invalid line break in line 1.
    tests/data/test_all_wrong.tsv:2:0: E1: Invalid line break in line 2.
    tests/data/test_all_wrong.tsv:3:0: E1: Invalid line break in line 3.
    ....

If you want to display a summary of the errors, you can further provide a `--summary` parameter:

.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv --summary

    tests/data/test_all_wrong.tsv:32:0: E4: Number of tabs in line 32 does not match tabs in header.
    tests/data/test_all_wrong.tsv:31:0: E9: Last row in file should be empty.

    ##### TSValid Summary #####

    Error: unexpected Line Break Encoding
     * count: 31
     * error_code: E1

    Error: number Of Tabs Check
     * count: 16
     * error_code: E4

    Error: leading Whitespace Check
     * count: 1
     * error_code: E2

    Error: empty Line
     * count: 1
     * error_code: E5

    Error: empty Last Row
     * count: 1
     * error_code: E9

If you wish to skip certain checks, you can use the --skip parameter like this:

.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv --skip E9 --skip E2

The above will run all TSValid checks apart from E9 and E2. You can also exclude checks using a
regular expression pattern like this:

.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv --skip E.* --summary

This will skip all checks that match the regex `^E.*$`.


Some TSV files come with commented lines. These can be explicitly skipped:

.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv --comment "#"

Any line thats starts with a comment character will be skipped this way.


By default, TSV files are opened under the assumption that they are UTF-8 encoded. This default behaviour can be changed:

.. code-block:: bash

    tsvalid tests/data/test_all_wrong.tsv --encoding "ascii"

