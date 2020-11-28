from datasize.__datasize__ import DataSize
__default_autoformat__ = '.3a'
import sys
from itertools import chain

def string_format_check(a,b,c):
    c = c.strip() # don't test leading spaces?!?!?
    try:
        assert a.format(DataSize(b)).strip() == c
    except AssertionError:
        sys.stderr.write("\nAssertion: '{}'.format(DataSize('{}')) == '{}'".format(a, b, c))
        sys.stderr.write("\nAssertionError: '{}' != '{}'\n".format(a.format(DataSize(b)), c))
        raise

def test_parse_and_format():
    from datasize.__expected_test_results__ import parse_and_format_results
    for example in parse_and_format_results.keys():
        for mode in DataSize._auto_fmt_modes.keys():
            formatted_string = parse_and_format_results[example]
            input_args = example[:3]
            output_format = example[3]
            parsed_string = '{}{}{}'.format(*input_args)
            format_code_str ='{{:{}}}'.format(output_format)
            yield string_format_check, format_code_str, parsed_string, formatted_string

def test_autoformat_defaults():
    yield string_format_check, '{:A}', '1000', '1000'
    yield string_format_check, '{:a}', '1000', '1KB'
    yield string_format_check, '{}', '1024', '1KiB'
    yield string_format_check, '{:B}', '1024', '1024B'

def test_bug_ticket_regressions():
    # https://github.com/aphor/datasize/issues/6
    assert DataSize('10KiB') == 10240
    assert DataSize('10kiB') == 10240

example_values = (1, 2, 4, 16, 64, 1024, 65536, 0.1, 0.25, 0.125, 56.65)
prefixes = list(DataSize.unit_prefixes.keys())
bases = ('B','b')
padchars, npads, fprecisions = (('','0'), (20, ''), (3,4))
fixed_cases = [{'n':n,'p':p,'b':b} for n in example_values for p in prefixes for b in bases]
auto_cases = [{'n':n,'p':p,'b':b} for n in (512,65536,64) for p in prefixes for b in ('', 'b')]

if __name__ == '__main__':
    ''' Save the output of this to __expected_test_results__.py to generate
        static test data. Check it manually, and make manual adjustments as necessary
        before running unit tests against it.'''
    print('parse_and_format_results = {')
    for i in chain(fixed_cases, auto_cases):
        for mode in (mode + base_unit for mode in chain(prefixes, DataSize._auto_fmt_modes.keys()) for base_unit in ('', 'B', 'b')):
            for padding in chain((''), ('{}{}.{}'.format(c,n,p) for c in padchars for n in npads for p in fprecisions)):
                i['DS'] = DataSize('{n}{p}{b}'.format(**i))
                i['m'] = padding + mode
                fmt_code_str = '"{{DS:{}}}"'.format(i['m'])
                print('\t'.join(('','({n},','"{p}",','"{b}",','"{m}"): ',fmt_code_str,',')).format(**i))
    print('}')
