# AtlantisBot

<a href="https://www.buymeacoffee.com/johnvictor" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

A discord bot made in Python using the [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) library made by Rapptz (rewrite version)

Made specifically for the discord server of the RuneScape 3 Clan Atlantis

***

## Self-hosting

- Not yet supported, and likely won't ever be, the bot is very customized to a specific discord server, do feel free, whoever, to copy features of it and implement them in your own bot ([license](LICENSE))

***

## Features

#### Tasks

- **Automated Team Maker** 
    - Gets information from the Bot's database for teams created with the `!team` command, such as which roles to allow to join a Team, listens for join (or leave) messages in the chat set with `!team` and automatically builds the Team with them
        - Also saves every message the Bot sent for join/leave messages so it can clear them all when a team is deleted by using the `!del <team ID>` command (Requires manage channels permission or be the Team creator)
        - Mark players as substitutes when they join over the Team limit number, automatically moving and notifying them when a slot opens up

 Joining a Team                              |  Team List                                  |
:-------------------------------------------:|:-------------------------------------------:|
![](/images/tasks/joining_team_example.png)  | ![](/images/tasks/created_team_example.png)                              |

- **Automated Raids (Game Event) Team Maker** 
    - Notifications for Raids one hour before reset every 2 days, bot picks up people who ask for invites to the Team and gathers them into a list (works the same as the team making command explained above)

- **Clan Adventurer's Log Feed**
    - Sends Adventurer's log entries of every player in a Clan to a specific discord channel by making use of [RuneScape 3's API](https://rs.wiki/API) by Jagex

Adventurer's Log messages example    |
:-----------------------------------:|
![](/images/tasks/advlog_example.png)|

- **Updated Merchant Stock**
    - Edits a message with the current [Travelling Merchant](https://runescape.wiki/w/Travelling_Merchant's_Shop) stock everytime it updates
    ![](/images/tasks/merchant.png)

***

#### Notable Commands

*Arguments format:* \<required\> (optional|default value)

- `!team` - Saves information about a Team that gets saved in the Bot's database, this information is used to automate team creation and joining of other people, explained in the automated team making task above

Using the Team command (gif)          |
:------------------------------------:|
![](/images/commands/team_creation_example.gif)|

- `!claninfo <player>` - Gets clan information from a RuneScape 3 player and returns it in a formatted embed (makes use of [RuneScape 3's](https://rs.wiki/API) API by Jagex)

Using the Claninfo command                |
:----------------------------------------:|
![](/images/commands/claninfo_example.png)|

- `!ranks` - Checks which rankings need to be updated in a RuneScape 3 Clan based on their Clan Exp (custom configuration)

Using the Ranks command                |
:-------------------------------------:|
![](/images/commands/ranks_example.png)|

- `!amigosecreto` - Join the Yearly Atlantis Secret Santa event, automatically pairs people and notifies them when the the pairing is done

Joining Secret Santa Successfully              |     Can't join if you aren't in the clan     |
:---------------------------------------------:|:---------------------------------------------|
![](/images/commands/amigo_secreto_success.png)| ![](/images/commands/amigo_secreto_fail.png) |

- `!comp (competition number|1) (number of players to list|10 (max=50))` - Gets information from a RuneClan Exp competition (or lists them if you've passed no arguments and there's more than one running)

Using the Comp command                | Listing competitions                          |
:------------------------------------:|:----------------------------------------------|
![](/images/commands/comp_example.png)|![](/images/commands/multiple_comp_example.png)|
