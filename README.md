# THM-Discord-Bot
TryHackMe Python Discord Bot

![alt text](/images/computer.png?raw=true "Box Bot Logo")

**Source:** Created by DarkStar7471 aka J0n


***Description:***

​A bot created for usage on the TryHackMe discord chat server.


***Related Hosting Links***

- TryHackMe Site: https://tryhackme.com


***Contributors***

- Robin
  - Early dev, room cog, social, gtfobins
- Paradox
  - Shibe, spaniel
- Yume
  - Boop and honk
- Dan @SherlockSec
  - Leaderboard generation, tweet command
- Horshark
  - Room cog, role sync, stats, rank, rules, help/staff, vote, giveaway, faq, jira, overall rewrite and improvement, database; utils; commands libs, minor features and fixes
- CMNatic
  - Housekeeping / general maintenance, integrating thm help site, feedback, vpnscript
- 5nake.exe
  - Exploitdb search
- szymex73
  - TryHackMe API call optimizations, leaderboard generation optimizations
- TuxTheXplorer
  - Cooctus
- Emma
  - Fixing BAC


***Commands:***
{required args} | [optional args]

> Verifying/Role Assigning Commands
verify {token} | Verify yourself to get your roles.

> Room
writeup {room_code} | Get the writeups for a room.
randomroom | Select a random room.

> Announcements
notifyme | Toggle the role to get notified on announcements.

> Leaderboard Commands
leaderboard [page] | Prints the leaderboard.
monthly [page] | Prints this month's leaderboard.

> Rank Commands
rank [@mention/username] | Get a THM member's rank.

> FAQ
vpn | Learn how to use OpenVPN to connect to our network!
multivpn | Learn how to look for duplicate instance of your OpenVPN connection.
vpnscript | Use our VPN troubleshooting script to diagnose common issues!

> Rules Commands
rules | Sends the rules.
rule {rule} | Sends the requested rule.

> Gtfobins
gtfobins [query] | Search GTFObins for a term.

> Social
github | Get the bot's Github link.
twitter | Get the Twitter link.
reddit | Get the Reddit link.
website | Get the Website link.
discord | Get the Discord invite.
social | Get links to all our socials.
tweet | Get THM's last tweet.

> Fun Commands
skidy | Sends Skidy's emote.
ashu | Send Ashu's emote.
dark | Send a random Darkstar quote.
honk | HOOONK!
boop {@user} | Boop someone!
noot | NOOT NOOT!
shibe | Sends a shibe picture.
spaniel | Sends a spaniel picture.
xkcd | Send a random XKCD comic.
cooctus | Sends a cooctus clan member.

> Help
staff | Displays all staff commands.
help | Displays all commands.

> Provide Feedback
feedback | Let us know what you think of TryHackMe!

> Utility
exploit [-Title][-CVE][-Type][-Platform][-Port][-Content][-Author][-Tag][-Help] {Query} | Searches exploit-db for exploits.

> Docs
docs [topic] | List our documented topics.
