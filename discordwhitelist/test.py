from rcon import RCON

rcon = RCON('localhost', '123')
rcon.connect()

print(rcon.command('whitelist remove zekrotja'))
print(rcon.command('whitelist remove luxtracon'))
