#!/usr/bin/python

# this was originally obtained from https://github.com/em-/python-vcd/blob/master/vcd/grammar.py and then
# modified to work with icarus verilog dumps

from pyparsing import (Word, Group, SkipTo, StringEnd,
                       Suppress, ZeroOrMore, Optional,
                       alphas, nums, alphanums, printables,
                       oneOf)

s = Suppress

identifier = Word(printables)('id')

definition = Word(alphas)('type') + Word(nums)('size') + \
             identifier + Word(printables)('name') + Optional('[' + Word(nums+':') + ']')('bussize')

signal = Group(s('$var') + definition + s('$end'))('signal')

content = SkipTo('$end')('content') + s('$end')
section = Group(s('$') + Word(alphas)('name') + content)('section')

unit = s('1') + oneOf('s ms ns us ps fs')
timescale = (s('$timescale') + unit + s('$end'))('timescale')

scope = Group(s('$scope module') + Word(printables)('module') + s('$end'))('scope')
scope_nonmodule = Group(s('$scope begin') + Word(printables)('module') + s('$end'))('scope')
upscope = Group(s('$upscope $end'))('upscope')

enddefinitions = s('$enddefinitions' + content)

time = s('#') + Word(nums)('time')

std_logic = oneOf('U X 0 1 Z W L H-')('std_logic')
std_logic_vector = Word('b', 'UX01ZWLH-')('std_logic_vector')

value = Group((std_logic | std_logic_vector) + identifier)('value')
step = Group(time + ZeroOrMore(value))

headers = signal | timescale | scope | scope_nonmodule | upscope
changes = enddefinitions + SkipTo(StringEnd())('steps') + StringEnd()

vcd = ZeroOrMore((headers | changes) | section)('vcd')
