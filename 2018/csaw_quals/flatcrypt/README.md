# challenge_name

## Challenge details
| Category | Points |
|:---------|-------:|
| crypto   | 100    |

### Description
> no logos or branding for this bug
> flag is not in flag format. flag is `PROBLEM_KEY`

## Write-up

This is a surprisingly subtle task for its point value.

The following runs on the server to which we connect:
```python
#!/usr/bin/python
import zlib
import os

from Crypto.Cipher import AES
from Crypto.Util import Counter

ENCRYPT_KEY = bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000')
# Determine this key.
# Character set: lowercase letters and underscore
PROBLEM_KEY = 'not_the_flag'

def encrypt(data, ctr):
    return AES.new(ENCRYPT_KEY, AES.MODE_CTR, counter=ctr).encrypt(zlib.compress(data))

while True:
    f = input("Encrypting service\n")
    if len(f) < 20:
        continue
    enc = encrypt(bytes((PROBLEM_KEY + f).encode('utf-8')), Counter.new(64, prefix=os.urandom(8)))
    print("%s%s" %(enc, chr(len(enc))))
```
We can manipulate a part of the plaintext
and we wish to recover it entirely from its AES-CTR ciphertext.
After spending a considerable amount of time researching potential pitfalls of AES-CTR,
we reach the conclusion that its usage here is as correct as it gets: random nonce,
sufficiently long counter. AES is resistant against known-plaintext attacks.
The encryption itself is probably uncrackable.

After looking over the code many times, we have to conclude that
the intended solution is somehow tied to the call to `zlib.compress`.
Is compression before encryption a bad practice?
A quick search suggests that no, it is, in fact, recommended.
The crucial bit of insight, which took its time coming to us, is this:
```python
>>> zlib.compress(b'not_the_flag')
b'x\x9c\xcb\xcb/\x89/\xc9H\x8dO\xcbIL\x07\x00 \x8e\x04\xeb'
>>> zlib.compress(b'not_the_flag' + b'random_text')
b'x\x9c\xcb\xcb/\x89/\xc9H\x8dO\xcbIL/J\xccK\xc9\xcf\x8d/I\xad(\x01\x00r*\t\x90'
>>> zlib.compress(b'not_the_flag' + b'not_the_flag')
b'x\x9c\xcb\xcb/\x89/\xc9H\x8dO\xcbIL\xcfCb\x03\x00|\x14\t\xd5'
```
Of course! By manipulating our part of plaintext, we can leak information
about its similarity with the flag via the length of the ciphertext.

This ought to do the job:
```python
from pwn import *

from string import ascii_lowercase

alphabet = ascii_lowercase + '_'

r = remote('crypto.chal.csaw.io', 8040)

guesses = ['']

while True:
  new_guesses = []
  for guess in guesses:
    for char in alphabet:
      pat = char + guess
      this = pat * max(int(20/len(pat)) + 1, 4)
      r.recvline()
      r.sendline(this)
      length = r.recvline()[-2]
      new_guesses.append((pat, length))
  best_len = min(new_guesses, key=lambda x: x[1])[1]
  guesses += [x[0] for x in filter(lambda x: x[1] == best_len, new_guesses)]
  max_len = max(map(len, guesses))
  guesses = list(filter(lambda x: len(x) == max_len, guesses))
  print(guesses, best_len)
```
Unforunately, this doesn't work as written:
the guess sequence it produces is just cycles of the word `go`:
```
o
go
ogo
gogo
ogogo
...
```
The situation seems almost hopeless at this point;
we never did find out if there is a better way to do this, but
an adequate solution turns out to be "guessing" that the flag ends with `logo`:
```
logo
_logo
a_logo  # Success! No longer in a loop!
...
```
####
```
crime_doesnt_have_a_logo
```
