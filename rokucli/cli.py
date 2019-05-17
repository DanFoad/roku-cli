import sys
import time
import argparse
from roku import Roku
from rokucli.discover import discover_roku
from blessed import Terminal


usage_menu = (
  "  +-------------------------------+-------------------------+\n"
  "  | Back           B or <Backsp>  | Replay          R       |\n"
  "  | Home           H              | Info/Settings   i       |\n"
  "  | Left           h or <Left>    | Rewind          r       |\n"
  "  | Down           j or <Down>    | Fast-Fwd        f       |\n"
  "  | Up             k or <Up>      | Play/Pause      <Space> |\n"
  "  | Right          l or <Right>   | Enter Text      /       |\n"
  "  | Ok/Enter       <Enter>        | Use Keyboard    u       |\n"
  "  +-------------------------------+-------------------------+\n"
  "   (press q to exit)\n")

keys = [
  [ '~', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '~' ],
  [ '~', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '~' ],
  [ 'C', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '@', '§' ],
  [ '~', '~', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '-', '_', '~' ],
  [ '~', '~', '~', '~', '~', '~', '~', ' ', '<', '>', '.', '~' ]
]

class RokuCLI():
  def __init__(self):
    self.term = Terminal()
    self.roku = None

  def parseargs(self):
    parser = argparse.ArgumentParser(
      description='Interactive command-line control of Roku devices')
    parser.add_argument(
      'ipaddr',
      nargs='?',
      help=('IP address of Roku to connect to. By default, will ' +
            'automatically detect Roku within LAN.'))
    return parser.parse_args()

  def text_entry(self):
    allowed_sequences = set(['KEY_ENTER', 'KEY_ESCAPE', 'KEY_DELETE'])

    sys.stdout.write('Enter text (<Esc> to abort) : ')
    sys.stdout.flush()

    # Track start column to ensure user doesn't backspace too far
    start_column = self.term.get_location()[1]
    cur_column = start_column

    with self.term.cbreak():
      val = ''
      while val != 'KEY_ENTER' and val != 'KEY_ESCAPE':
        val = self.term.inkey()
        if not val:
          continue
        elif val.is_sequence:
          val = val.name
          if val not in allowed_sequences:
            continue

        if val == 'KEY_ENTER':
          self.roku.enter()
        elif val == 'KEY_ESCAPE':
          pass
        elif val == 'KEY_DELETE':
          self.roku.backspace()
          if cur_column > start_column:
            sys.stdout.write(u'\b \b')
            cur_column -= 1
        else:
          self.roku.literal(val)
          sys.stdout.write(val)
          cur_column += 1
        sys.stdout.flush()

      # Clear to beginning of line
      sys.stdout.write(self.term.clear_bol)
      sys.stdout.write(self.term.move(self.term.height, 0))
      sys.stdout.flush()

  def use_keyboard(self):
    allowed_sequences = set(['KEY_ENTER', 'KEY_ESCAPE', 'KEY_DELETE'])

    sys.stdout.write('Enter text (<Esc> to abort) : ')
    sys.stdout.flush()

    # Track start column to ensure user doesn't backspace too far
    start_column = self.term.get_location()[1]
    cur_column = start_column

    with self.term.cbreak():
      val = ''
      sequence = ''
      while val != 'KEY_ENTER' and val != 'KEY_ESCAPE':
        val = self.term.inkey()
        if not val:
          continue
        elif val.is_sequence:
          val = val.name
          if val not in allowed_sequences:
            continue

        if val == 'KEY_ENTER':
          self.type_keys(sequence)
        elif val == 'KEY_ESCAPE':
          pass
        elif val == 'KEY_DELETE':
          sequence = sequence[:-1]
          if cur_column > start_column:
            sys.stdout.write(u'\b \b')
            cur_column -= 1
        else:
          sequence += val
          sys.stdout.write(val)
          cur_column += 1
        sys.stdout.flush()

      # Clear to beginning of line
      sys.stdout.write(self.term.clear_bol)
      sys.stdout.write(self.term.move(self.term.height, 0))
      sys.stdout.flush()

  def type_keys(self, sequence):
    initial = '1'
    normalised_sequence = ''
    for k in sequence:
      if k.isupper():
        normalised_sequence += 'C' + k.lower() + 'C'
      else:
        normalised_sequence += k
    normalised_sequence += '§'

    for k in normalised_sequence:
      pos = (self.find_key(initial))
      while pos != (-1, -1):
        pos = self.step_to(pos, self.find_key(k))
      initial = k

  def step_to(self, start, end):
    if start[0] != end[0]:
      m = 1 if start[0] < end[0] else -1
      if keys[start[0] + m][start[1]] != '~':
        self.move_vertical(m)
        return (start[0] + m, start[1])
    if start[1] != end[1]:
      m = 1 if start[1] < end[1] else -1
      if keys[start[0]][start[1] + m] != '~':
        self.move_horizontal(m)
        return (start[0], start[1] + m)
    self.roku.select()
    if keys[end[0]][end[1]] == 'C':
      time.sleep(1)
    return (-1, -1)

  def move_vertical(self, m):
    if m == 1:
      self.roku.down()
    else:
      self.roku.up()

  def move_horizontal(self, m):
    if m == 1:
      self.roku.right()
    else:
      self.roku.left()

  def find_key(self, k):
    for i in range(len(keys)):
      for j in range(len(keys[i])):
        if keys[i][j] == k:
          return (i, j)
    return (-1, -1)

  def run(self):
    ipaddr = self.parseargs().ipaddr

    # If IP not specified, use Roku discovery and let user choose
    if ipaddr:
      self.roku = Roku(ipaddr)
    else:
      self.roku = discover_roku()

    if not self.roku:
      return

    print(usage_menu)

    cmd_func_map = {
      'B':          self.roku.back,
      'KEY_DELETE': self.roku.back,
      'H':          self.roku.home,
      'h':          self.roku.left,
      'KEY_LEFT':   self.roku.left,
      'j':          self.roku.down,
      'KEY_DOWN':   self.roku.down,
      'k':          self.roku.up,
      'KEY_UP':     self.roku.up,
      'l':          self.roku.right,
      'KEY_RIGHT':  self.roku.right,
      'KEY_ENTER':  self.roku.select,
      'R':          self.roku.replay,
      'i':          self.roku.info,
      'r':          self.roku.reverse,
      'f':          self.roku.forward,
      ' ':          self.roku.play,
      '/':          self.text_entry,
      'u':          self.use_keyboard}

    # Main interactive loop
    with self.term.cbreak():
      val = ''
      while val.lower() != 'q':
        val = self.term.inkey()
        if not val:
          continue
        if val.is_sequence:
          val = val.name
        if val in cmd_func_map:
          try:
            cmd_func_map[val]()
          except:
            print('Unable to communicate with roku at ' +
              str(self.roku.host) + ':' + str(self.roku.port))
            sys.exit(1)


def main():
  RokuCLI().run()

if __name__ == '__main__':
  main()
