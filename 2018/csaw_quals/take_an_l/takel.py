from pwn import *
import subprocess

r = remote('misc.chal.csaw.io', 9000)

r.recvuntil('marked block: ')
blk = eval(r.recvline())  # we trust our csaw overlords

res = subprocess.check_output(['./tile', str(blk[0]), str(blk[1])])
r.send(res)

print(r.recvall().rstrip().decode('utf8'))
