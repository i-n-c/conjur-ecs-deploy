#!/usr/bin/env python3

#pybisect


# 1 Known good
# 2
# 3
# 4
# 5 <--- First test, success
# 6
# 7 <-- Second test, success
# 8 <-- Third test, fail
# 9 <-- Fourth test, success.
# 10 Known Bad

# result = 10 is the first bad version

# Selector, pick middle version and round down.

import json
import math
import os

import click

class BisectFile():
    def __init__(self, input_path):
        self.input_path = input_path
        self.state_path = f"{input_path}.bisect_state"
        self.state = []
        self.read_or_create_state_file()

    def write_state_file(self):
        with open(self.state_path, 'w') as state_file:
            state_file.write(json.dumps(self.state))

    def read_or_create_state_file(self):
        if not os.path.exists(self.state_path):
            with open(self.input_path) as input:
                self.state = [
                            {'linenumber': ln,
                             'content': content,
                             'status': ''}
                            for ln, content in enumerate(input.readlines())
                        ]
            self.write_state_file()

        with open(self.state_path) as state_file:
            state = json.load(state_file)
            # ensure state is sorted by line number on read.
            state.sort(key=lambda line: line['linenumber'])
            self.state = state

    def line_number_for_content(self, content):
        return list(filter(lambda line: line['content'].strip() == content.strip(), self.state))[0]

    def set_line_status(self, content, status):
        line = self.line_number_for_content(content)
        line['status'] = status
        self.state[line['linenumber']] = line
        self.write_state_file()

    def next_line(self):
        # Determine which line should be tested next.
        good_lines = list(filter(lambda l: l['status'] == 'good', self.state))
        bad_lines = list(filter(lambda l: l['status'] == 'bad', self.state))
        if len(good_lines) < 1 or len(bad_lines) < 1:
            raise Exception('At least one good and one bad line must be set'
                            ' before the next line to test can be calculated')

        # 1 good min_good
        # 2
        # 3 good max_good
        # 4
        # 5 bad min_bad
        # 6 bad max_bad

        # 1 bad min_bad
        # 2
        # 3 bad max_bad
        # 4
        # 5 good min_good
        # 6 good max_good

        min_good = min([l['linenumber'] for l in good_lines])
        max_good = max([l['linenumber'] for l in good_lines])
        min_bad = min([l['linenumber'] for l in bad_lines])
        max_bad = max([l['linenumber'] for l in bad_lines])

        # print(f"min_good: {min_good}, max_good:{max_good}")
        # print(f"min_bad: {min_bad}, max_bad:{max_bad}")

        if max_good < min_bad:
            # good at top of file (find lowest value of min_bad)
            if max_good + 1 == min_bad:
                return {'message': "Bisect complete, first bad "
                        f"version is: {self.state[min_bad]['content'].strip()}"}

            next_index = math.floor((min_bad - max_good)/2) + max_good
        else:
            # bad at top
            if max_bad + 1 == min_good:
                return {'message': "Bisect complete, first bad "
                        f"version is: {self.state[max_bad]['content'].strip()}"}
            next_index = math.floor((min_good - max_bad)/2) + max_bad

        return self.state[next_index]


@click.group()
@click.pass_context
@click.option('--file', 'input_file', help="Path to input file", required=True)
def cli(ctx, input_file):
    """ Program for running bisection on an arbitrary input file

    To start mark one line in a file good and another bad with
    mark-good and mark-bad. Then request the next line to test
    with next-line. When the test is complete mark that line,
    and request the next line until the next-line call announces
    that bisect is complete.

    Example session:

    \b
    # Mark initial range
    $ ./listbisect.py --file test_in.txt mark-good --line 4.3.8
    $ ./listbisect.py --file test_in.txt mark-bad --line 3.12.5
    # Request next line, test and mark the result
    $ ./listbisect.py --file test_in.txt next-line
    4.3.0
    $ ./listbisect.py --file test_in.txt mark-bad --line 4.3.0
    # Repeat until the end
    $ ./listbisect.py --file test_in.txt next-line
    4.3.5
    $ ./listbisect.py --file test_in.txt mark-good --line 4.3.5
    $ ./listbisect.py --file test_in.txt next-line
    4.3.3
    $ ./listbisect.py --file test_in.txt mark-bad --line 4.3.3
    $ ./listbisect.py --file test_in.txt next-line
    4.3.4
    $ ./listbisect.py --file test_in.txt mark-bad --line 4.3.4
    $ ./listbisect.py --file test_in.txt next-line
    Bisect complete, first bad version is: 4.3.4
    Bisect Summary:
    4.3.8 good
    4.3.7
    4.3.6
    4.3.5 good
    4.3.4 bad
    4.3.3 bad
    4.3.1
    4.3.0 bad
    4.2.1
    4.2.0
    4.1.1
    4.1.0
    4.0.1
    4.0.0
    3.12.6
    3.12.5 bad
    """
    ctx.obj = {'bf': BisectFile(input_file)}

@cli.command()
@click.pass_obj
@click.option('--line', 'content',
              help="Contens of the line to be marked as good",
              required=True)
def mark_good(ctx, content):
    """ Mark a line as good """
    ctx['bf'].set_line_status(content, 'good')

@cli.command()
@click.pass_obj
@click.option('--line', 'content',
              help="Contens of the line to be marked as bad",
              required=True)
def mark_bad(ctx, content):
    """ Mark a line as bad """
    ctx['bf'].set_line_status(content, 'bad')

@cli.command()
@click.pass_obj
def next_line(ctx):
    """ Show the next line to be tested """
    next_line = ctx['bf'].next_line()
    if 'message' in next_line:
        print(next_line['message'])
        print('Bisect Summary:')
        for line in ctx['bf'].state:
            print(f"{line['content'].strip()} {line['status']}")
    else:
        print(next_line['content'].strip())


cli()