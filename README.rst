roku-cli
========

Interactively control your Roku device from the command-line with vim-style key bindings.

Forked from https://github.com/ncmiller/roku-cli because I wanted to type on the keyboard too

Installation
------------
::

   git clone https://github.com/danfoad/roku-cli.git
   cd roku-cli
   python setup.py install

Supported with Python 3 on Linux and Mac OS. Also works with Cygwin on
Windows. Sorry, no native Windows support.

Usage
-------

To launch the CLI::

    python3 ./rokucli/cli.py 10.0.0.0

But replace with the IP address of the Roku box

From there, you'll be in interactive mode, and you can input keys to control
your Roku::

    +-------------------------------+-------------------------+
    | Back           B or <Backsp>  | Replay          R       |
    | Home           H              | Info/Settings   i       |
    | Left           h or <Left>    | Rewind          r       |
    | Down           j or <Down>    | Fast-Fwd        f       |
    | Up             k or <Up>      | Play/Pause      <Space> |
    | Right          l or <Right>   | Enter Text      /       |
    | Ok/Enter       <Enter>        | Use keyboard    u       |
    +-------------------------------+-------------------------+
    (press q to exit)


Using the keyboard
-------

To type on the keyboard, select the input field on screen so that the on-screen keyboard appears. Press u and then enter the string that you want the keyboard to type and then press enter. The keyboard must be focused on the 1 key initially in order for the typing to work

N.B. Symbols currently don't work

