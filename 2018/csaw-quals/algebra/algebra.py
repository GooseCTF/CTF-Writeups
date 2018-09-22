from pwn import *

class ex:
    def __init__(self):
        self.factor = 1
        self.constant = 0
    def __mul__(self, rhs):
        self.constant *= rhs
        self.factor *= rhs
        return self
    def __div__(self, rhs):
        self.constant /= rhs
        self.factor /= rhs
        return self
    def __add__(self, rhs):
        self.constant += rhs
        return self
    def __sub__(self, rhs):
        self.constant -= rhs
        return self
    def __rmul__(self, lhs):
        self.constant *= lhs
        self.factor *= lhs
        return self
    def __rdiv__(self, lhs):
        self.constant = lhs / self.constant
        self.factor = lhs / self.factor
        return self
    def __radd__(self, lhs):
        self.constant += lhs
        return self
    def __rsub__(self, lhs):
        self.factor = -self.factor
        self.constant = lhs - self.constant
        return self
    def __str__(self):
        return '%d * X %c %d' % (self.factor, '-' if self.constant < 0 else '+',
                                 abs(self.constant))

def solve(expr):
    lhs, rhs = expr.split(b' = ')
    x = eval(lhs, {'X' : ex()})
    rhs = float(rhs)
    if abs(x.factor - 0) > 1e-6:
        return (rhs - x.constant) / x.factor
    else:
        return 42

def mayberound(n):
    if (abs(n - round(n)) < 1e-6):
        return round(n)
    else:
        return n

r = remote('misc.chal.csaw.io', 9002)
r.recvuntil('*')
r.recvline()

while True:
    question = r.recvline()
    print(question.rstrip().decode('utf8'))
    answer = mayberound(solve(question))
    print(answer)
    r.recvuntil(': ')
    r.sendline(str(answer))
    r.recvline()
