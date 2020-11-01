from math import ceil
import sys


def __bits_to_bytes__(b, word_length=8):
    '''count bytes filled for a number of bits with a given or default (8)
           bit word length
        >>> bits_to_bytes(4)
        >>> 1

        >>> bits_to_bytes(4, word_length=4)
        >>> 1

        >>> bits_to_bytes(256)
        >>> 32

        >>> bits_to_bytes(256, word_length=16)
        >>> 16

        >>> bits_to_bytes(1024, word_length=4)
        >>> 256
    '''
    B = ceil(b/word_length)
    return int(B)


if sys.version_info[0] < 3:
    __DataSize_super__ = long
else:
    __DataSize_super__ = int


class DataSize(__DataSize_super__):
    '''Integer subclass that handles units appropriate for data allocation.
    https://www.iso.org/standard/31898.html
    https://physics.nist.gov/cuu/Units/binary.html
    
    Adapts popular string representations of data sizes to integer values
    supporting arithmetic and alternate string representations.
    Internally represents data amounts as an integer count of bytes.
    Parses strings given as constructor values, and also provides
    string.format() support for human-readable data quantities expressed
      in metric and IEC unit multiples of
        bytes: (suffix ending in 'B') or
        bits: (suffix ending in 'b')
      like 10.4TB or 128kb
    The minimum granularity is in bytes, defined as 8 bit words by default.
    Objects constructed from non integers will be rounded up to the nearest
      byte.

    Arithmetic methods inherit directly from int, and return int. This
      keeps this class smaller, and avoids unecessary constructor overhead.

    WARNING: in Python 2, DataSize is a subclass of long to avoid overflows
      on large values. Upgrade!
    '''
    word_length = 8  # defaults to octet = byte for conversion to/from bits
    bit_suffix, byte_suffix = 'b', 'B'
    autoformat_prefixes = ('a', 'A')
    metric_prefixes = {
        # metric/decimal unit prefixes
        'k': 1000,
        'M': 1000**2,
        'G': 1000**3,
        'T': 1000**4,
        'P': 1000**5,
        'E': 1000**6,
        'Z': 1000**7,
        'Y': 1000**8,
        }
    IEC_prefixes = {
        # binary IEC unit prefixes
        'Ki': 1024,
        'Mi': 1024**2,
        'Gi': 1024**3,
        'Ti': 1024**4,
        'Pi': 1024**5,
        'Ei': 1024**6,
        'Zi': 1024**7,
        'Yi': 1024**8,
        }
    nonstandard_prefixes = dict(zip(
            (k[0] for k in IEC_prefixes.keys()),
            (m for m in IEC_prefixes.values())
            ))
    unit_prefixes = metric_prefixes.copy()
    unit_prefixes.update(IEC_prefixes)
    # also make a map from unit denominations to prefix
    prefix_units = dict(zip(
        tuple(unit_prefixes.values()), tuple(unit_prefixes.keys())))
    nonstandard_units = dict(zip(
        (m for m in IEC_prefixes.values()),
        (k[0] for k in IEC_prefixes.keys())))

    def __init__(self, spec, word_length=8):
        '''Usage:
        min_heap = DataSize('768Mib')
        max_heap = DataSize('2G')
        max_heap - min_heap = high_memory_warning_limit
        sys_mem = DataSize('16GiB')
        disk_sz = DataSize('650GB')
        baud = DataSize('25Mb')

        Optional keyword argument 'word_length' can be used
        to specify some other bits per byte than the default of 8.
        '''
        self.word_length = int(word_length)

    def __new__(subclass, spec, **kwargs):
        '''Because DataSize is a subclass of int, we must override __new__()
        to implement a string decoder that can provide an immutable integer
        value for instances.
        '''
        word_length = int(kwargs.get('word_length', DataSize.word_length))
        unit = 'bytes'
        multiple = 1
        raw = spec[:]
        if raw[-1] == DataSize.bit_suffix:
            unit = 'bits'
        raw = raw.rstrip(DataSize.bit_suffix).rstrip(DataSize.byte_suffix)
        units = list(DataSize.unit_prefixes.keys())
        units.sort(reverse=True)
        for prefix in units:
            offset = len(prefix)
            if raw[-offset:] == prefix:
                raw = raw[:-offset]
                multiple = DataSize.unit_prefixes[prefix]
                break

        if raw[-1] in DataSize.autoformat_prefixes: #rstrip autoformat_prefixes
            raw = raw[:-1]
        raw_number = float(raw)
        if unit == 'bits':
            bits = raw_number * multiple
            value = __bits_to_bytes__(bits)
        else:
            bits = raw_number * word_length * multiple
            value = raw_number * multiple

        if isinstance(value, float):
            value = ceil(value)

        return __DataSize_super__.__new__(DataSize, value)

    def __format__(self, code):
        '''formats as a decimal number, but recognizes data units as type
        format codes.Precision is ignored for integer multiples of the unit
        specified in the format code.format codes:
        a    autoformat will choose a unit defaulting to the largest
              size with a quantity >= 1 (default)
        A    abbreviated number of bytes (implied IEC units of 'B' bytes)
        B    bytes      (1)
        KiB  kibibytes  (1024)
        kB   kilobytes  (1000)
        ...
        GiB  Gibibytes  (1024**3)
        GB   Gigabytes  (10**9)
        ...
        YiB  Yobibytes  (1024**8)
        YB   Yottabytes (10**24)

        >>> from datasize import DataSize
        >>> 'My new {:GB} SSD really only stores {:.2GiB} of data.'.format(
                DataSize('750GB'),DataSize(DataSize('750GB') * 0.8))
        'My new 750GB SSD really only stores 558.79GiB of data.'
        '''
        base_unit = ''
        prefix = ''
        denomination = 1
        multiple = 1
        auto_modes = self.autoformat_prefixes
        suffix_rpad_spaces = 0
        prefix_units = self.prefix_units
        if not code or code[-1] == 'a':
            fmt_mode = 'a'
        elif code[-1] == 'A':
            fmt_mode = 'A'
            base_unit = ''
        else:
            fmt_mode = None

        if fmt_mode in auto_modes:  # automatically choose a denomination/unit
            if fmt_mode == 'A':
                prefix_units = self.nonstandard_units
                suffix_rpad_spaces = max(
                        [len(k) for k in prefix_units.values()]
                    )
            else:
                base_unit = 'B'
                suffix_rpad_spaces = 1 + max(
                        [len(k) for k in prefix_units.values()]
                    )
            code = code.rstrip(''.join(auto_modes))
            denominations = list(prefix_units.keys())
            denominations.sort(reverse=True)
            for quantity in denominations:
                if self * multiple >= quantity:
                    prefix = prefix_units[quantity]
                    denomination = quantity
                    break
        else:
            if code[-1] in ('b', 'B'):
                base_unit = code[-1]
                suffix_rpad_spaces += 1
                code = code[:-1]  # eat the base unit
                if base_unit == 'b':
                    multiple = self.word_length

            units = list(self.unit_prefixes.keys())
            units.sort(reverse=True)
            for prefix in units:
                offset = len(prefix)
                if code[-offset:] == prefix:
                    suffix_rpad_spaces += offset
                    code = code[:-offset]
                    denomination = self.unit_prefixes[prefix]
                    break
                prefix, denomination = '', 1
        value = float(self * multiple)/float(denomination)

        if value.is_integer():  # emit integers if we can do it cleanly
            code = code.split('.', 1)[0]  # precision in the code? strip it
            if code:
                code = '{c}{n}'.format(
                                        c=code[0],
                                        n=(int(code) - suffix_rpad_spaces))
            code += 'd'
            def cast(x): return int(x)

        else:
            if code and '.' in code:
                fpad, fprecision = code.split('.', 1)
                if fpad:
                    padchar = fpad[0]
                else:
                    padchar = ''
                if fpad:
                    npad = int(fpad) - suffix_rpad_spaces
                else:
                    npad = ''
                code = '{c}{pad}.{prec}'.format(
                                                c=padchar,
                                                pad=npad,
                                                prec=fprecision)
            code += 'f'
            def cast(x): return x

        unit_suffix_template = '{{:<{n}}}'.format(n=suffix_rpad_spaces)
        unit_output_suffix = unit_suffix_template.format(prefix + base_unit)
        format_parms = {'code': code, 'unit': unit_output_suffix}
        template = '{{:{code}}}{unit}'.format(**format_parms)
        return template.format(cast(float(value)))
