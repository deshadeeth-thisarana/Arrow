# The Arrow bot

All Errors are now fixed and the bot is working fine..

![Arrowbot](https://telegra.ph/file/2ebd3d2bf6db41a457bfd.jpg)


*A Modular Group management Bot on Sinhala*

# ❤Support❤

<a href="https://t.me/gangoffriendschannel"><img src="https://img.shields.io/badge/Join-Telegram%20Channel-red.svg?logo=Telegram"></a>

<a href="https://t.me/gangoffriends"><img src="https://img.shields.io/badge/Join-Telegram%20Group-blue.svg?logo=telegram"></a>

# THE EASY WAY to Deploy 

_*Follow the methods carefully*_

1) Create an account at https://heroku.com


2) Create a new bot from [BotFather](t.me/BotFather) and copy its api token

      ![Arrow](https://telegra.ph/file/5a199b6ee7eb7ce0569a1.jpg)


3) Click "Deploy" button below👇

      [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/deshadeeth-thisarana/Arrow)


4) Give an app name (It must contain only simple letters)

      ![Arrow](https://telegra.ph/file/33a9172ef2e8d19b016bc.jpg)


5) Enter your API_HASH and API_ID (You can get it from "https://my.telegram.org/")

      ![Arrow](https://telegra.ph/file/ef4a1e62b4aeaab1a975d.jpg)


6) Enter CASH_API_KEY required for currency converter (You can get a api_key from "https://www.alphavantage.co/support/#api-key")

      ![Arrow](https://telegra.ph/file/6ca229633ecf5763d539a.jpg)


7) Enter the ID of the group that note down important bot level events (It must be a public group and the bot should be added to that group)
 
      ![Arrow](https://telegra.ph/file/bbdbf9ac5840e0f60c06c.jpg)
           👆You should enter same id to this two spaces👆
 

8) Enter TIME_API_KEY required for timezone information (You can get a key from "https://timezonedb.com/api")

      ![Arrow](https://telegra.ph/file/3b7d1d07929fcfb10f885.jpg)


9) Enter the Api token that you obtain from [BotFather](t.me/BotFather) in the "Token" space 

      ![Arrow](https://telegra.ph/file/a00ac13c0d3a75aa910b4.jpg)


10) Enter url of the your Heroku app as "https://<your_app_name>.herokuapp.com/" (Enter your app name without "<" and ">"😁)

       ![Arrow](https://telegra.ph/file/86c945c478f693b618217.jpg)

#*A message for Experts*
   - Always you can change the owner name id and other settings when publishing..
   - The bots owner infomations present at Emilia/Modules/Lang/id.py and en.py.
   - Paste your coffeehouse api to activate your own chatbot.
   - You can remove entry Daisy logo in Main.py.
   - Link your Credit card to Heroku for get extra amount of dynos.
     
#*I am just a learner and this is the code I used as Rose bot
```
<details>
<summary>-THE HARD WAY of deploying -</summary>



# Starting the bot.

Once you've setup your database and your configuration (see below) is complete, simply run:

`python3 -m tg_bot`


##Setting up the bot (Read this before trying to use!):
Please make sure to use python3.6, as I cannot guarantee everything will work as expected on older python versions!
This is because markdown parsing is done by iterating through a dict, which are ordered by default in 3.6.

###Configuration

There are two possible ways of configuring your bot: a config.py file, or ENV variables.

The prefered version is to use a `config.py` file, as it makes it easier to see all your settings grouped together.
This file should be placed in your `tg_bot` folder, alongside the `__main__.py` file . 
This is where your bot token will be loaded from, as well as your database URI (if you're using a database), and most of 
your other settings.

It is recommended to import sample_config and extend the Config class, as this will ensure your config contains all 
defaults set in the sample_config, hence making it easier to upgrade.

An example `config.py` file could be:
```
from tg_bot.sample_config import Config


##Class Development(Config):
    
    OWNER_ID = 254318997  # my telegram ID
    OWNER_USERNAME = "DeshadeethThisarana"  # my telegram username
    API_KEY = "your bot api key"  # my api key, as provided by the botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database'  # sample db credentials
    MESSAGE_DUMP = '-1234567890' # some group chat that your bot is a member of
    USE_MESSAGE_DUMP = True
    SUDO_USERS = [18673980, 83489514]  # List of id's for users which have sudo access to the bot.
    LOAD = []
    NO_LOAD = ['translation']
```

##If you can't have a config.py file (EG on heroku), it is also possible to use environment variables.
##The following env variables are supported:
 
 - `ENV`: Setting this to ANYTHING will enable env variables

 - `TOKEN`: Your bot token, as a string.
 - `OWNER_ID`: An integer of consisting of your owner ID
 - `OWNER_USERNAME`: Your username

 - `DATABASE_URL`: Your database URL
 - `MESSAGE_DUMP`: optional: a chat where your replied saved messages are stored, to stop people deleting their old 
 - `LOAD`: Space separated list of modules you would like to load
 - `NO_LOAD`: Space separated list of modules you would like NOT to load
 - `WEBHOOK`: Setting this to ANYTHING will enable webhooks when in env mode
 messages
 - `URL`: The URL your webhook should connect to (only needed for webhook mode)

 - `SUDO_USERS`: A space separated list of user_ids which should be considered sudo users
 - `SUPPORT_USERS`: A space separated list of user_ids which should be considered support users (can gban/ungban,
 nothing else)
 - `WHITELIST_USERS`: A space separated list of user_ids which should be considered whitelisted - they can't be banned.
 - `DONATION_LINK`: Optional: link where you would like to receive donations.
 - `CERT_PATH`: Path to your webhook certificate
 - `PORT`: Port to use for your webhooks
 - `DEL_CMDS`: Whether to delete commands from users which don't have rights to use that command
 - `STRICT_GBAN`: Enforce gbans across new groups as well as old groups. When a gbanned user talks, he will be banned.
 - `WORKERS`: Number of threads to use. 8 is the recommended (and default) amount, but your experience may vary.
 __Note__ that going crazy with more threads wont necessarily speed up your bot, given the large amount of sql data 
 accesses, and the way python asynchronous calls work.
 - `BAN_STICKER`: Which sticker to use when banning people.
 - `ALLOW_EXCL`: Whether to allow using exclamation marks ! for commands as well as /.

###Python dependencies

Install the necessary python dependencies by moving to the project directory and running:

`pip3 install -r requirements.txt`.

This will install all necessary python packages.

###Database

If you wish to use a database-dependent module (eg: locks, notes, userinfo, users, filters, welcomes),
you'll need to have a database installed on your system. I use postgres, so I recommend using it for optimal compatibility.

In the case of postgres, this is how you would set up a the database on a debian/ubuntu system. Other distributions may vary.

- install postgresql:

`sudo apt-get update && sudo apt-get install postgresql`

- change to the postgres user:

`sudo su - postgres`

- create a new database user (change YOUR_USER appropriately):

`createuser -P -s -e YOUR_USER`

This will be followed by you needing to input your password.

- create a new database table:

`createdb -O YOUR_USER YOUR_DB_NAME`

Change YOUR_USER and YOUR_DB_NAME appropriately.

- finally:

`psql YOUR_DB_NAME -h YOUR_HOST YOUR_USER`

This will allow you to connect to your database via your terminal.
By default, YOUR_HOST should be 0.0.0.0:5432.

You should now be able to build your database URI. This will be:

`sqldbtype://username:pw@hostname:port/db_name`

Replace sqldbtype with whichever db youre using (eg postgres, mysql, sqllite, etc)
repeat for your username, password, hostname (localhost?), port (5432?), and db name.

##Modules
###Setting load order.

The module load order can be changed via the `LOAD` and `NO_LOAD` configuration settings.
These should both represent lists.

If `LOAD` is an empty list, all modules in `modules/` will be selected for loading by default.

If `NO_LOAD` is not present, or is an empty list, all modules selected for loading will be loaded.

If a module is in both `LOAD` and `NO_LOAD`, the module will not be loaded - `NO_LOAD` takes priority.

### Creating your own modules.

Creating a module has been simplified as much as possible - but do not hesitate to suggest further simplification.

All that is needed is that your .py file be in the modules folder.

To add commands, make sure to import the dispatcher via

`from tg_bot import dispatcher`.

You can then add commands using the usual

`dispatcher.add_handler()`.

Assigning the `__help__` variable to a string describing this modules' available
commands will allow the bot to load it and add the documentation for
your module to the `/help` command. Setting the `__mod_name__` variable will also allow you to use a nicer, user
friendly name for a module.

The `__migrate__()` function is used for migrating chats - when a chat is upgraded to a supergroup, the ID changes, so 
it is necessary to migrate it in the db.

The `__stats__()` function is for retrieving module statistics, eg number of users, number of chats. This is accessed 
through the `/stats` command, which is only available to the bot owner.
</details>

 
