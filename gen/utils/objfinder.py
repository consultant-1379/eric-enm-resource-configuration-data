'''
This file helps the finding keys in a yaml file.
'''
from io import StringIO
from typing import Any
import re


class _CodeBuilder:
    '''
    Builds the code.
    '''
    def __init__(self) -> None:
        self._code = StringIO()
        self._ind = 0

    def line(self, line: str) -> None:
        '''
        Write line to StringIO.
        '''
        for _ in range(self._ind):
            self._code.write('    ')
        self._code.write(line)
        self._code.write('\n')

    def inc(self) -> None:
        '''
        Increase the index by 1.
        '''
        self._ind += 1

    def dec(self) -> None:
        '''
        Decrements the index by 1.
        '''
        self._ind -= 1

    def get(self) -> str:
        '''
        Gets the value of _code.
        '''
        return self._code.getvalue()


def _gen(code: _CodeBuilder, opathsp, val='d'):
    '''
    This function is the implementation of code generation.
    '''
    if opathsp:
        value = opathsp.pop(0)
        if value == '*':
            code.line(f"if type({val}) == list:")
            code.inc()
            code.line("for e in d:")
            code.inc()
            _gen(code, opathsp, 'e')
            code.dec()
            code.dec()
        else:
            musthave = False
            if value[-1] == '!':
                value = value[:-1]
                musthave = True
            code.line(f"if type({val}) == dict and '{value}' in {val}:")
            code.inc()
            code.line(f"d = {val}['{value}']")
            _gen(code, opathsp)
            code.dec()
            if musthave:
                code.line('else:')
                code.inc()
                code.line(f"re.append(KeyError('{value}', {val}))")
                code.dec()
    else:
        code.line(f"re.append({val})")


def objfinder(opath: str) -> Any:
    '''
    Finds the key value in a json file.
    '''
    opathsp = []
    listresult = False
    for json_key_value in re.findall(r'[^"\.][^\.]*|".+?"\!?', opath):
        json_key_value = json_key_value.replace('"', '')
        opathsp.append(json_key_value)
        if json_key_value == '*':
            listresult = True

    code = _CodeBuilder()
    code.line('def f(d):')
    code.inc()
    code.line("re = []")
    _gen(code, opathsp)
    if listresult:
        code.line('return re')
    else:
        code.line('return re[0] if re else None')
    # code.print()
    ctx = {}
    exec(code.get(), None, ctx)
    return ctx['f']
