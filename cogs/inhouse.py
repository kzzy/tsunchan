from discord.ext import commands
import re
import random

"""Global Variables"""
inhouse_active = False  # Boolean Used for !inhouse series of commands
inhouse_started = False  # Boolean Used to check for in-progress inhouse sessions
inhouse_ready = False  # Ready state once total players are met
inhouse_game = ""
inhouse_players = []  # List for !inhouse players
inhouse_current = 0  # Current amount of players
inhouse_total = 0  # Total amount players
inhouse_t1 = []  # List for Team 1 players
inhouse_t2 = []  # List for Team 2 players
inhouse_t1_slots = 0  # Team 1 total slots
inhouse_t2_slots = 0  # Team 2 total slots
inhouse_channels = {'Lobby': '395892786999721986',  # Lobby     ID
                    'Channel 1': '395897418094215168',  # Channel 1 ID
                    'Channel 2': '395897458032377859'  # Channel 2 ID
                    }

class Inhouse:

    def __init__(self, bot):
        self.bot = bot

    def check_role(self, member, target):
        """ Helper function to validate given member with given target role"""
        for role in member.roles:
            if str(role) == target:
                return True
        return False

    def print_ih(self, instruct : str, input_1="", input_2="", input_3="", input_4=""):
        """ Helper Function to organize text printing"""
        txt = ""

        if instruct == "teams":
            t1 = "TEAM 1"
            t2 = "TEAM 2"
            txt += "`{:<35}{}`".format(t1, t2)
            txt += '\n'
            for player_t1, player_t2 in zip(inhouse_t1, inhouse_t2):
                txt += "`{:<35}{}`".format(player_t1.display_name, player_t2.display_name)
                txt += '\n'

        elif instruct == "ready_help":
            txt += "```Commands\n!inhouse move to start the match\n!inhouse scramble to randomize teams again.\n!inhouse swap <p1> <p2> to swap specific players.```"

        elif instruct == "help":
            txt += 'Invalid inhouse command\nPlease refer to **!help inhouse**'

        elif instruct == "improper_permissions":
            txt += 'You do not have the proper permissions to join/manage the inhouse'

        elif instruct == "inactive_inhouse":
            txt += 'There is no active inhouse currently going.\nPlease refer to **!help inhouse**'

        elif instruct == "init_inhouse":
            txt += '**{0}** has started an inhouse.\n```{1}\t({2} VS {3})```'.format(input_1, input_2, input_3, input_4)

        elif instruct == "commence_inhouse":
            txt += '**Inhouse is ready to commence**\n\n`Type in \'!inhouse start\' to begin`'

        elif instruct == "inprogress_inhouse":
            txt += 'There is an inhouse in-progress. Please wait until it\'s done.'

        elif instruct == "no_inprogress_inhouse":
            txt += 'There is no inhouse in-progress.'

        elif instruct == "end_match":
            txt += 'The current match has ended... Moving players back to the Lobby'

        elif instruct == "not_enough_queue":
            txt += 'There are not enough players in the queue.'

        elif instruct == "full_inhouse":
            txt += 'Sorry the inhouse is currently full. Baka!'

        elif instruct == "end_inhouse":
            txt += 'The current inhouse session ended.'

        elif instruct == "not_found":
            txt += "There are no players found with your search key: **{0}**".format(input_1)

        # Unique Cases #
        elif instruct == "init_illegal_team_slots":
            txt += "The team numbers are illegal, must be > 0"

        elif instruct == "swap_too_many_cases":
            txt += "There are numerous players with the same names in Team 1. (**{0}**)\nRefine your search, then try again.".format(input_1)

        elif instruct == "swap_result":
            txt += "Swapped Players: **{0}** and **{1}**".format(input_1, input_2)

        elif instruct == "scramble":
            txt += '{0} has scrambled the teams! The new teams are below.\n'.format(input_1)

        elif instruct == "join_queue":
            txt += '**{0}** has joined the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3)

        elif instruct == "leave_queue_too_many_cases":
            txt += 'There are numerous players with the same names in the queue. (**{0}**)\nRefine your search, then try again.'.format(input_1)

        elif instruct == "leave_queue":
            txt += '**{0}** has left the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3)

        elif instruct == "leave_queue_auto":
            txt += '**{0}** has automatically left the queue, [{1} / {2}] players needed\n`Left the inhouse channels`'.format(input_1, input_2, input_3)

        elif instruct == "already_in_queue":
            txt += '{0} has already joined this queue.'.format(input_1)

        elif instruct == "not_in_queue":
            txt += '{0} never joined the queue in the first place.'.format(input_1)
        return txt

    @commands.group(pass_context=True)
    async def inhouse(self, ctx):
        """Inhouse System"""
        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            await self.bot.say(self.print_ih("improper_permissions"))
            return

        # Validate subcommand usage
        if ctx.invoked_subcommand is None:
            await self.bot.say(self.print_ih("help"))
        return

    @inhouse.command(pass_context=True)
    async def init(self, ctx, game: str, t1_slots: str, t2_slots: str):
        """Initializes inhouse"""
        global inhouse_active
        global inhouse_total
        global inhouse_t1_slots
        global inhouse_t2_slots
        global inhouse_game

        # Parameter Check
        if int(t1_slots) < 1 or int(t2_slots) < 1:
            await self.bot.say(self.print_ih('init_illegal_team_slots'))
            return

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is True:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        inhouse_active = True
        inhouse_game = game
        inhouse_t1_slots = t1_slots
        inhouse_t2_slots = t2_slots
        inhouse_total = int(t1_slots) + int(t2_slots)

        await self.bot.say(self.print_ih('init_inhouse', member.display_name, inhouse_game, t1_slots, t2_slots))

    @inhouse.command(pass_context=True)
    async def start(self, ctx):
        """Starts a match"""
        global inhouse_active
        global inhouse_started
        global inhouse_ready
        global inhouse_players

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if inhouse is full and ready to go
        if inhouse_ready is False:
            await self.bot.say(self.print_ih('not_enough_queue'))
            return

        # Check if there is an inhouse in-progress
        if inhouse_started is True:
            await self.bot.say(self.print_ih('inprogress_inhouse'))
            return

        cur_t1_slots = 0
        inhouse_started = True

        # While there are still players not on any teams
        while inhouse_players:
            # Random players onto team 1 and once full, throw rest into team 2
            randy = random.choice(inhouse_players)
            inhouse_players.remove(randy)
            inhouse_t1.append(randy)
            cur_t1_slots += 1

            # Enough players on team 1
            if cur_t1_slots == int(inhouse_t1_slots):

                # Fill rest players into team 2
                while inhouse_players:
                    inhouse_t2.append(inhouse_players.pop())

        # Print team rosters
        #  Sort alphabetically
        inhouse_t1.sort(key=lambda x: x.display_name)
        inhouse_t2.sort(key=lambda x: x.display_name)
        await self.bot.say(self.print_ih("ready_help") + '\n' + self.print_ih("teams"))

    @inhouse.command(pass_context=True)
    async def join(self, ctx):
        """Joins the queue"""
        global inhouse_players
        global inhouse_current

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check if readied already
        if member in inhouse_players:
            await self.print_ih('already_in_queue', member.display_name)
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if inhouse is already full
        if (inhouse_current == inhouse_total):
            await self.bot.say(self.print_ih('full_inhouse'))
            return

        # Update player list and counters
        inhouse_players.append(member)
        inhouse_current += 1

        # Check for if enough players have ready'd post-addition
        if (inhouse_current == inhouse_total):
            global inhouse_ready
            inhouse_ready = True
            await self.bot.say(self.print_ih('join_queue', member.display_name, inhouse_current, inhouse_total) + '\n' + self.print_ih("commence_inhouse"))
        else:
            await self.bot.say(self.print_ih('join_queue', member.display_name, inhouse_current, inhouse_total))

    @inhouse.command(pass_context=True)
    async def unjoin(self, ctx, player=None):
        """Leaves the queue"""
        global inhouse_ready
        global inhouse_players
        global inhouse_current

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Find player if optional arg is given #
        if player is not None:
            target = ""
            # Regex to match all found names for team 1
            player_pattern = r'((' + re.escape(player.lower()) + r')+(.)*)'
            matches = [x for x, x in enumerate(inhouse_players) if re.search(player_pattern, x.display_name.lower())]

            # Return first player match of exact string
            for x in matches:
                if x.display_name.lower() == player.lower() or len(matches) == 1:
                    target = x
                    break

            # If numerous matches, but no name exactly matches the given string
            if len(matches) > 1 and not target:
                dupe = ','.join(str(x.display_name) for x in matches)
                await self.bot.say(self.print_ih('leave_queue_too_many_cases', dupe))
                return
            elif len(matches) < 1:
                await self.bot.say(self.print_ih('not_found', player))
                return

            # Set player to actual member object if pass all checks
            player = target

        # Check if member readied originally
        if member not in inhouse_players and player is None:
            await self.bot.say(self.print_ih('not_in_queue', member.display_name))
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Update player list and counters
        inhouse_current -= 1
        if player is not None:
            inhouse_players.remove(player)
            await self.bot.say(self.print_ih('leave_queue', player.display_name, inhouse_current, inhouse_total))
        else:
            inhouse_players.remove(member)
            await self.bot.say(self.print_ih('leave_queue', member.display_name, inhouse_current, inhouse_total))

        # Update inhouse status
        if inhouse_ready is True:
            inhouse_ready = False

    @inhouse.command(pass_context=True)
    async def swap(self, ctx, t1_name: str, t2_name: str):
        """Swaps two players"""
        global inhouse_t1
        global inhouse_t2

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if inhouse is full and ready to go
        if inhouse_ready is False:
            await self.bot.say(self.print_ih('not_enough_queue'))
            return

        # Check if there is an inhouse in-progress
        if inhouse_started is False:
            await self.bot.say(self.print_ih('no_inprogress_inhouse'))
            return

        # Find Team 1 PLAYER #
        t1_player = None  # Team 1 Target Player
        # Regex to match all found names for team 1
        p1_pattern = r'((' + re.escape(t1_name.lower()) + r')+(.)*)'
        t1_matches = [x for x, x in enumerate(inhouse_t1) if re.search(p1_pattern, x.display_name.lower())]

        # Return first player match of exact string
        for x in t1_matches:
            if x.display_name.lower() == t1_name.lower() or len(t1_matches) == 1:
                t1_player = x
                break

        # If numerous matches, but no name exactly matches the given string
        if len(t1_matches) > 1 and t1_player is None:
            t1_dupe = ','.join(str(x.display_name) for x in t1_matches)
            await self.bot.say(self.print_ih('swap_too_many_cases', t1_dupe))
            return
        elif len(t1_matches) < 1:
            await self.bot.say(self.print_ih('not_found', t1_name))
            return

        # Find Team 2 PLAYER #
        t2_player = None  # Team 2 Target Player
        # Regex to match all found names for team 2
        p2_pattern = r'((' + re.escape(t2_name.lower()) + r')+(.)*)'
        t2_matches = [x for x, x in enumerate(inhouse_t2) if re.search(p2_pattern, x.display_name.lower())]

        # Return first player match of exact string
        for x in t2_matches:
            if x.display_name.lower() == t2_name.lower() or len(t2_matches) == 1:
                t2_player = x
                break

        # If numerous matches, but no name exactly matches the given string
        if len(t2_matches) > 1 and t2_player is None:
            t2_dupe = ','.join(str(x.display_name) for x in t2_matches)
            await self.bot.say(self.print_ih('swap_too_many_cases', t2_dupe))
            return
        elif len(t2_matches) < 1:
            await self.bot.say(self.print_ih('not_found', t2_name))
            return

        # Swap respective players and print new teams
        if t1_player is not None and t2_player is not None:
            p1_index = inhouse_t1.index(t1_player)
            p2_index = inhouse_t2.index(t2_player)

            inhouse_t2.append(inhouse_t1.pop(p1_index))
            inhouse_t1.append(inhouse_t2.pop(p2_index))

            # Print updated teams
            inhouse_t1.sort()  # Sort alphabetically
            inhouse_t2.sort()
            await self.bot.say(self.print_ih('ready_help')+'\n'+self.print_ih('swap_result', t1_player.display_name, t2_player.display_name)+'\n\n'+self.print_ih('teams'))

    @inhouse.command(pass_context=True)
    async def move(self, ctx):
        """Moves teams"""
        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if inhouse is full and ready to go
        if inhouse_ready is False:
            await self.bot.say(self.print_ih('not_enough_queue'))
            return

        # Check if there is an inhouse in-progress
        if inhouse_started is False:
            await self.bot.say(self.print_ih('no_inprogress_inhouse'))
            return

        # Move players into their respective inhouse voice channels
        for player in inhouse_t1:
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 1")))
        for player in inhouse_t2:
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 2")))


    @inhouse.command(pass_context=True)
    async def scramble(self, ctx):
        """Scrambles teams"""

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if inhouse is full and ready to go
        if inhouse_ready is False:
            await self.bot.say(self.print_ih('not_enough_queue'))
            return

        # Check if there is an inhouse in-progress
        if inhouse_started is False:
            await self.bot.say(self.print_ih('no_inprogress_inhouse'))
            return

        cur_t1_slots = 0

        # Reset team 1 and team 2 rosters
        while inhouse_t1:
            inhouse_players.append(inhouse_t1.pop())
        while inhouse_t2:
            inhouse_players.append(inhouse_t2.pop())

        # While there are still players not on any teams
        while inhouse_players:
            # Random players onto team 1 and once full, throw rest into team 2
            randy = random.choice(inhouse_players)
            inhouse_players.remove(randy)
            inhouse_t1.append(randy)
            cur_t1_slots += 1

            # Enough players on team 1
            if cur_t1_slots == int(inhouse_t1_slots):

                # Fill rest players into team 2
                while inhouse_players:
                    inhouse_t2.append(inhouse_players.pop())

        # Print team rosters
        inhouse_t1.sort()  # Sort alphabetically
        inhouse_t2.sort()
        await self.bot.say(self.print_ih('scramble', member.display_name) + '\n' + self.print_ih('ready_help') + '\n' + self.print_ih("teams"))

    @inhouse.command(pass_context=True)
    async def end(self, ctx):
        """Concludes a match"""

        global inhouse_active
        global inhouse_started
        global inhouse_ready
        global inhouse_players

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check for active inhouse
        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        # Check if there is an inhouse in-progress
        if inhouse_started is False:
            await self.bot.say(self.print_ih('no_inprogress_inhouse'))
            return

        # Check if inhouse is full and ready to go
        if inhouse_ready is False:
            await self.bot.say(self.print_ih('not_enough_queue'))
            return

        inhouse_started = False
        # Move members back to the main lobby channel
        for player in inhouse_t1:
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Lobby")))
        for player in inhouse_t2:
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Lobby")))

        # Reset team 1 and team 2 rosters
        while inhouse_t1:
            inhouse_players.append(inhouse_t1.pop())
        while inhouse_t2:
            inhouse_players.append(inhouse_t2.pop())

        await self.bot.say(self.print_ih('end_match'))

    @inhouse.command(pass_context=True)
    async def finish(self, ctx):
        """Concludes inhouse"""
        global inhouse_active
        global inhouse_started
        global inhouse_ready
        global inhouse_current
        global inhouse_total
        global inhouse_players
        global inhouse_t1_slots
        global inhouse_t2_slots
        global inhouse_game

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        if inhouse_active is True:
            # Reset variables
            inhouse_active = False
            inhouse_started = False
            inhouse_ready = False
            inhouse_current = 0
            inhouse_total = 0
            inhouse_t1_slots = 0
            inhouse_t2_slots = 0
            inhouse_game = ""
            del inhouse_players[:]  # Delete current list of players
            del inhouse_t1[:]
            del inhouse_t2[:]
            await self.bot.say(self.print_ih('end_inhouse'))
        else:
            await self.bot.say(self.print_ih('inactive_inhouse'))

def setup(bot):
    bot.add_cog(Inhouse(bot))