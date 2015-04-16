class FactString(object):
    
    def __init__(self, string):
        self._s = string
    
    def __cmp__(self, other):
        if self._s > str(other):
            return 1
        elif self._s < str(other):
            return -1
        else:
            return 0
    
    def __mul__(self, other):
        if type(other) == int:
            return FactString(self._s * other)
        elif isinstance(other, FactString):
            return FactString(self._s * int(other._s[-1]))
        else:
            raise TypeError("unsupported operand type(s) for *: FactString and {}".format(type(other)))
    
    def __sub__(self, other):
        return FactString(self._s[:-1] + chr(ord(self._s[-1])-other))
    
    def __len__(self):
        return len(self._s)
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'FactString({!r})'.format(self._s)

def fact(i):
    if i >= 1:
        return i * fact(i - 1)
    else:
        return 1


if __name__ == '__main__':
    print "fact(4) => {}".format(fact(4))
    print "fact(FactString('4')) => {}".format(fact(FactString("4")))
