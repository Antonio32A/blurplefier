=========
Blurplefy
=========

Bot which converts images to different blurple shades or other colors.
This bot is a modified fork which works on multiple servers, has the rollteam command, it doesn't have docker and it uses JSON config.
This bot might have more bugs.

-------
Running
-------

First you have to create a config file with credentials, you can simply copy the ``example-config.json`` and
edit it with your own values, then save it as ``config.json``.

To run the bot you will need to install and run `Redis <https://redis.io>`_ (see
`here <https://redislabs.com/blog/redis-on-windows-10/>`_ for Windows 10 instructions) as well as
install all the Python requirements using ``pip install -Ur requirements.txt``.

Running the bot and worker can then be done from the root directory of this repository:

.. code-block :: bash

    python -m bot

    python -m worker

And that's it! Have fun with the bot.
