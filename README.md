# Alexa-WoL-Skill
## Introduction
**THIS IS NOT A SKILL MEANT TO BE PUBLISHED** - Watch out! This skill has **NO** user-management functions!

Since the skill sends WoL packets on **LAYER 2**, the server that hosts the skill **MUST BE ON THE SAME NETWORK AS THE DEVICE YOU WANT TO TURN ON!** (yes, that's why the skill isn't meant to be published).

The skill is meant to always stay in development mode: the skill sends a WoL signal to a device on the local network via magic packet. If you create the dev account on your account, you'll be able to use the skill on your devices.

## Requirements
- An Alexa dev account
- A server on the same network as the device you want to turn on

## Initial setup/Usage
### Alexa
To get started, you'll need an [Amazon Developer account](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/create-developer-account.html).

Once you get it, create a Skill with a custom model, self-provisioned and from scratch.

![Setup1](https://user-images.githubusercontent.com/22529815/188335765-61338a20-9825-49fd-acf3-80bb9b6c1e0a.png)
![Setup2](https://user-images.githubusercontent.com/22529815/188335793-a6f1b9d8-8476-44e0-a0e3-ac09ba4c2f6e.png)

Set an invocation name and check if you have those intents:

![Setup3](https://user-images.githubusercontent.com/22529815/188335909-5ee770f8-b5ef-48da-8a4d-38b7c32aab3d.png)

To enable the Italian language open the language dropdown menu and select "Language settings"

![Setup4](https://user-images.githubusercontent.com/22529815/188335962-815cc9d4-884b-4f7e-8ad8-6fffd78688f1.png)

### Python
Now, install the Python requirements with `pip3 install -r requirements.txt`, edit the `run.py` file and set the `__MAC_ADDRESS__` variable to the MAC address of the device you want to turn on. Now, just run it!
