from pwn import *

from string import ascii_lowercase

alphabet = ascii_lowercase + '_'

r = remote('crypto.chal.csaw.io', 8040)

guess = 'logo'

while True:
  new_guesses = []
  for char in alphabet:
    pat = char + guess
    this = pat * max(int(20/len(pat)) + 1, 4)
    r.recvline()
    r.sendline(this)
    length = r.recvline()[-2]
    new_guesses.append((pat, length))
  guess = min(new_guesses, key=lambda x: x[1])[0]
  print(guess)
