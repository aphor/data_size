from datasize.__datasize__ import DataSize
__default_autoformat__ = ' 20.4a'
import sys

def string_format_check(a,b,c):
    try:
        assert a.format(DataSize(b)) == c
    except AssertionError:
        sys.stderr.write("\nAssertionError: {} != {}\n".format(a.format(DataSize(b)), c))
        raise

def test_parse_and_format():
    from datasize.__expected_test_results__ import parse_and_format_results
    for example in parse_and_format_results.keys():
        formatted_string = parse_and_format_results[example]
        parsed_string = '{}{}{}'.format(*example)
        format_code_str ='{{:{}}}'.format(__default_autoformat__)
        yield string_format_check, format_code_str, parsed_string, formatted_string
        
def test_autoformat_defaults():
    yield string_format_check, '{:A}', '1024', '1k'
    yield string_format_check, '{}', '1024', '1KiB'
    yield string_format_check, '{:B}', '1024', '1024B'
    yield string_format_check, '{}', '1', '1B  ' # todo: https://github.com/aphor/datasize/issues/6

example_values = (1, 2, 4, 16, 64, 1024, 65536, 0.1, 0.25, 0.125, 56.65)
prefixes = list(DataSize.unit_prefixes.keys())
bases = ('B','b')
fixed_cases = [{'n':n,'p':p,'b':b} for n in example_values for p in prefixes for b in bases]
auto_cases = [{'n':n,'p':p,'b':b} for n in (512,65536,64) for p in ('a','A') for b in ('', 'b')]

if __name__ == '__main__':
    ''' Save the output of this to __expected_test_results__.py to generate
        static test data. Check it manually, and make manual adjustments as necessary
        before running unit tests against it.'''
    print('parse_and_format_results = {')
    for i in fixed_cases:
        i['DS'] = DataSize('{n}{p}{b}'.format(**i))
        fmt_code_str = '"{{DS:{}}}"'.format(__default_autoformat__)
        print('\t'.join(('','({n},','"{p}",','"{b}"):',fmt_code_str,',')).format(**i))
    for i in auto_cases:
        i['DS'] = DataSize('{n}{b}'.format(**i))
        fmt_code_str = '"{{DS:{}}}"'.format(__default_autoformat__)
        print('\t'.join(('','({n},','"{p}",','"{b}"):',fmt_code_str,',')).format(**i))
    print('}')
