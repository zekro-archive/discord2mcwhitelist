# discord2mcwhitelist

Leight Discord bot which binds Discord Accounts to Minecraft User IDs (Usernames) and manages the Minecraft Servers whitelist depending on this via RCON, so no server side mods are required.
  
## Installation and Usage

> Because this script is using [type annotations](https://www.python.org/dev/peps/pep-0484), you will need to use Python version 3.5 or above.

1. Clone the repository:
```
$ git clone https://github.com/zekroTJA/discord2mcwhitelist .
```

2. Install dependencies via pip:
```
$ python3 -m pip install -r requirements.txt
```

3. Execute the script with your configuration:
```
$ python3 discordwhitelist/main.py \
    --token YOUR_DISCORD_BOT_TOKEN \
    --prefix \> \
    --rcon-address localhost:25575 \
    --rcon-password YOUR_RCON_PASSWORD \
    --log-level 20
```

If you want to use the provided `Dockerfile`:

```
$ docker build . -t discord2mcwhitelist:latest
```

> `ENTRYPOINT` is set to `["python3", "discordwhitelist/main.py"]` so just apss your configuration parameters as startup command.
```
$ docker run --name dc2mcwl discord2mcwhitelist:latest \
    --token YOUR_DISCORD_BOT_TOKEN \
    --prefix \> \
    --rcon-address localhost:25575 \
    --rcon-password YOUR_RCON_PASSWORD \
    --log-level 20
```

---

© 2020 Ringo Hoffmann (zekro Development)  
Covered by the MIT Licence.
