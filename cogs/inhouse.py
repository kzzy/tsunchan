from discord.ext import commands
import re
import random
import itertools

"""Global Variables"""
inhouse_active = False  # Boolean Used for !inhouse series of commands
inhouse_started = False  # Boolean Used to check for in-progress inhouse sessions
inhouse_ready = False  # Ready state once total players are met
inhouse_get_start = False # If started with get function, set True (program behaves differently than from join)
inhouse_game = "" # Inhouse game name
inhouse_players = []  # List for !inhouse players
inhouse_current = 0  # Current amount of players
inhouse_total = 0  # Total amount players
inhouse_t1 = []  # List for Team 1 players
inhouse_t2 = []  # List for Team 2 players
inhouse_t1_slots = 0  # Team 1 total slots
inhouse_t2_slots = 0  # Team 2 total slots
inhouse_channels = {'Lobby' : '395892786999721986',      # Lobby     ID
                    'Channel 1' : '395897418094215168',  # Channel 1 ID
                    'Channel 2' : '395897458032377859',  # Channel 2 ID
                    }
inhouse_mode = "" # Current Inhouse Mode
inhouse_modes = {'standard' : False, # Hold mode names and boolean vals
                 'captains' : False}

class Inhouse:
    def __init__(self, bot):
        self.bot = bot
        self.prev_t1 = []

    def search_player(self, player, location):
        """ Helper function to search for member_object given player_name and search location
            Returns the player member object if found, or None if not found"""

        target = ""
        # Regex to match all found names for team 1
        player_pattern = r'((' + re.escape(player.lower()) + r')+(.)*)'
        matches = [x for x, x in enumerate(location) if re.search(player_pattern, x.display_name.lower())]

        # Return first player match of exact string
        for x in matches:
            if x.display_name.lower() == player.lower() or len(matches) == 1:
                target = x
                break

        # If numerous matches, but no name exactly matches the given string
        # RETURN respective error codes
        if len(matches) > 1 and not target:
            # Multiple matches were found
            return -1
        elif len(matches) < 1:
            # No matches were found
            return 0

        # Found target match
        return target

    def check_role(self, member, target):
        """ Helper function to validate given member with given target role"""
        for role in member.roles:
            if str(role) == target:
                return True
        return False

    def print_ih(self, instruct : str, input_1="", input_2="", input_3="", input_4="", input_5=""):
        """ Helper Function to organize text printing"""
        txt = ""
        if instruct == "teams":
            t1 = "TEAM 1"
            t2 = "TEAM 2"
            txt += "`{:<35}{}`".format(t1, t2)
            txt += '\n'
            for player_t1,player_t2 in itertools.zip_longest(inhouse_t1, inhouse_t2):
                if player_t1 is None:
                    txt += '    \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t' # Lack of Embedding options
                    txt += "`{:>35}`".format(player_t2.display_name)
                elif player_t2 is None:
                    txt += "`{}`".format(player_t1.display_name)
                else:
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
            txt += '**{0}** has started an inhouse.\n```GAME: {1}\nMODE: {2}\nTYPE: {3} VS {4}```'.format(input_1, input_2, input_3, input_4, input_5)

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
            txt += 'Exited Inhouse session.'

        elif instruct == "not_found":
            txt += "There were multiple names found based on your search"

        elif instruct == "too_many_cases":
            txt += 'There are multiple players with the same names. \nRefine your search, then try again.'

        # Unique Cases #
        elif instruct == "init_illegal_team_slots":
            txt += "The team numbers are illegal, must be > 0"

        elif instruct == "init_illegal_team_slots_captains":
            txt += "The team numbers are illegal, the setup must be a 5 vs 5!"

        elif instruct == "swap_result":
            txt += "Swapped Players: **{0}** and **{1}**".format(input_1, input_2)

        elif instruct == "scramble":
            txt += '{0} has scrambled the teams! The new teams are below.\n'.format(input_1)

        elif instruct == "join_queue":
            txt += '**{0}** has joined the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3)

        elif instruct == "leave_queue":
            txt += '**{0}** has left the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3)

        elif instruct == "leave_queue_auto":
            txt += '**{0}** has automatically left the queue, [{1} / {2}] players needed\n`Left the inhouse channels`'.format(input_1, input_2, input_3)

        elif instruct == "already_in_queue":
            txt += '{0} has already joined this queue.'.format(input_1)

        elif instruct == "not_in_queue":
            txt += '{0} never joined the queue in the first place.'.format(input_1)

        elif instruct == "ready_help_rematch":
            txt += "```Commands\n!inhouse move to start the match\n!inhouse scramble to randomize teams again.\n!inhouse swap <p1> <p2> to swap specific players.\n\nREMATCH Called by {0}!```".format(input_1)

        elif instruct == "no_prev_game":
            txt += 'There was no previous game played.\nActually play a game then request a rematch!'
            
        elif instruct == "enough_players_get":
            txt += 'Total No. of members match with Inhouse total, "!inhouse start" to begin'.format(input_1)

        elif instruct == "invalid_mode":
            txt += 'The given mode: **{0}** for the Inhouse is invalid.'.format(input_1)

        return txt

    @commands.group(pass_context=True, aliases=['ih'])
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
    async def init(self, ctx, game: str, t1_slots: str, t2_slots: str, mode: str):
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

        # Set Inhouse Mode
        mode = mode.lower()
        if(mode in inhouse_modes):
            inhouse_mode = mode

            if inhouse_mode == 'standard':
                inhouse_modes.update({"standard": True})
                mode = "Standard" # Fix text for printing
            elif inhouse_mode == 'captains':
                # Slot checking for ONLY 5 VS 5
                if int(t1_slots) != 1 and int(t2_slots) != 1:
                    await self.bot.say(self.print_ih('init_illegal_team_slots_captains'))
                    return
                else:
                    inhouse_modes.update({"captains": True})
                    mode = "Captain's Mode"
        else:
            # Invalid mode detected
            await self.bot.say(self.print_ih('invalid_mode', mode))
            return

        inhouse_active = True
        inhouse_game = game
        inhouse_t1_slots = t1_slots
        inhouse_t2_slots = t2_slots
        inhouse_total = int(t1_slots) + int(t2_slots)

        await self.bot.say(self.print_ih('init_inhouse', member.display_name, inhouse_game, mode, t1_slots, t2_slots))

    def standard_setup(self):
        """ Handle setup for STANDARD mode"""
        global inhouse_players

        cur_t1_slots = 0
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

    def captains_setup(self, *captains):
        for i in captains:
            print(i)
        return

    @inhouse.command(pass_context=True)
    async def start(self, ctx, *args):
        # Optional Params are for captains mode
        global inhouse_started

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

        inhouse_started = True

        if inhouse_modes.get('captains') is True:
            self.captains_setup(args) # Pass args to the captains_setup func

        # For any other cases, DEFAULT to Standard
        else:
            self.standard_setup()
        await self.bot.say(self.print_ih("ready_help") + '\n' + self.print_ih("teams"))

    @inhouse.command(pass_context=True, aliases=['rm'])
    async def rematch(self, ctx):
        """Starts a rematch"""
        global inhouse_started

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

        # Check if this is the 1st game, meaning there was not a previous game
        # If there is anything in prev_t1, then there was a previous game
        if not self.prev_t1:
            await self.bot.say(self.print_ih('no_prev_game'))
            return

        cur_t1_slots = 0
        inhouse_started = True

        # While there are still players not on any teams
        while inhouse_players:
            # For each unique player, loop through the inhouse players list to find that player
            # ASSUMES ALL PLAYERS ARE STILL PRESENT !!!
            for player_name in self.prev_t1:
                player = [person for person in inhouse_players if person.display_name == player_name]
                inhouse_players.remove(player[0])
                inhouse_t1.append(player[0])
                cur_t1_slots += 1

            # Enough players on team 1
            if cur_t1_slots == int(inhouse_t1_slots):

                # Fill rest players into team 2
                while inhouse_players:
                    inhouse_t2.append(inhouse_players.pop())

        del self.prev_t1[:] # Delete old team history

        # Print team rosters
        #  Sort alphabetically
        inhouse_t1.sort(key=lambda x: x.display_name)
        inhouse_t2.sort(key=lambda x: x.display_name)
        await self.bot.say(self.print_ih("ready_help_rematch", member.display_name) + '\n' + self.print_ih("teams"))
        
    @inhouse.command(pass_context=True, aliases=['j'])
    async def join(self, ctx):
        """Joins the queue"""
        global inhouse_players
        global inhouse_current

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Check if readied already
        #if member in inhouse_players:
        #    await self.bot.say(self.print_ih('already_in_queue', member.display_name))
        #    return

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

    @inhouse.command(pass_context=True, aliases=['uj'])
    async def unjoin(self, ctx, player=None):
        """Leaves the queue"""
        global inhouse_ready
        global inhouse_players
        global inhouse_current

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        # Set player to actual member object if pass all checks
        player = self.search_player(player, inhouse_players)

        # Check for any error codes returned
        if(player == -1):
            await self.bot.say(self.print_ih('too_many_cases'))
            return
        elif(player == 0):
            await self.bot.say(self.print_ih('not_found'))
            return

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
        t1_player = self.search_player(t1_name, inhouse_t1) # Team 1 Target Player

        # Check for any error codes returned
        if(t1_player == -1):
            await self.bot.say(self.print_ih('too_many_cases'))
            return
        elif(t1_player == 0):
            await self.bot.say(self.print_ih('not_found'))
            return

        # Find Team 2 PLAYER #
        t2_player = self.search_player(t2_name, inhouse_t2) # Team 2 Target Player

        # Check for any error codes returned
        if(t2_player == -1):
            await self.bot.say(self.print_ih('too_many_cases'))
            return
        elif(t2_player == 0):
            await self.bot.say(self.print_ih('not_found'))
            return

        # Swap respective players and print new teams
        if t1_player is not None and t2_player is not None:
            p1_index = inhouse_t1.index(t1_player)
            p2_index = inhouse_t2.index(t2_player)

            inhouse_t2.append(inhouse_t1.pop(p1_index))
            inhouse_t1.append(inhouse_t2.pop(p2_index))

            # Print updated teams
            inhouse_t1.sort(key=lambda x: x.display_name) # Sorting Alphabetically
            inhouse_t2.sort(key=lambda x: x.display_name)
            await self.bot.say(self.print_ih('ready_help')+'\n'+self.print_ih('swap_result', t1_player.display_name, t2_player.display_name)+'\n\n'+self.print_ih('teams'))

    @inhouse.command(pass_context=True, aliases=['mv'])
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
        inhouse_t1.sort(key=lambda x: x.display_name)  # Sorting Alphabetically
        inhouse_t2.sort(key=lambda x: x.display_name)
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
        # Appending the inhouse_player currently messes up the get function
        # The reason being is hard to figure out. However, appending to inhouse_players
        # ends up duping players.
        while inhouse_t1:
            if inhouse_get_start is True:
                inhouse_t1.pop()
            else:
                t1_player = inhouse_t1.pop()
                self.prev_t1.append(t1_player.display_name) # Keep track of old t1 players incase of rematch cmd * ONLY NEED 1 TEAMS ROSTER TO KNOW BOTH
                inhouse_players.append(t1_player)
        while inhouse_t2:
            if inhouse_get_start is True:
                inhouse_t2.pop()
            else:
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
            inhouse_modes.update({"standard": False})
            inhouse_modes.update({"captains": False})
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
            del self.prev_t1[:]
            await self.bot.say(self.print_ih('end_inhouse'))
        else:
            await self.bot.say(self.print_ih('inactive_inhouse'))

    @inhouse.command(pass_context=True)
    async def get(self, ctx):
        """Shortcut inhouse init"""
        # This function gets a player list based off the people who are in voice channel Inhouse
        # It allows the option to start the inhouse if the player list gathers the correct amount of people
        # specified by the initialization.

        # Updates list based on players in channel
        global inhouse_ready
        global inhouse_players
        global inhouse_current
        global inhouse_get_start

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
           return

        # Get Channel Member
        channel = self.bot.get_channel(inhouse_channels.get("Lobby"))

        if inhouse_active is False:
            await self.bot.say(self.print_ih('inactive_inhouse'))
            return

        if inhouse_started is True:
            await self.bot.say(self.print_ih("inprogress_inhouse"))
            return

        # Role Check for all members
        for x in range(0, len(channel.voice_members)):
            voice_member = channel.voice_members[x]
            if voice_member.roles == "Inhouse" is False:
                return

        #Updates inhouse_players when role check passes
        for x in channel.voice_members:
            inhouse_players.append(x)
        inhouse_current = len(inhouse_players)

        txt = ""
        #Prints Player list
        txt += 'Player List: '
        txt += '\n'
        for x in range(0, inhouse_current):
            inhousemember = inhouse_players[x]
            txt += inhousemember.display_name
            txt += '\n'

        # Tests if the inhouse_current matches with the inhouse specified in initialization
        if inhouse_current is inhouse_total:
            inhouse_ready = True
            inhouse_get_start = True
            txt += self.print_ih('enough_players_get')
        else:
            inhouse_ready = False
            txt += 'You need ' + str(inhouse_total-inhouse_current) + ' more players'

        await self.bot.say(txt)

    @inhouse.command(pass_context=True, hidden=True)
    async def status(self, ctx):
        """Debug Function"""

        # Extracts names from member class
        player_list = []
        player_t1_list = []
        player_t2_list = []

        for x in range(0, len(inhouse_players)):
            player_list.append(inhouse_players[x].display_name)

        for x in range(0, len(inhouse_t1)):
            player_t1_list.append(inhouse_t1[x].display_name)

        for x in range(0, len(inhouse_t2)):
            player_t2_list.append(inhouse_t2[x].display_name)

        # Displays statuses in a list in discord
        await self.bot.say('inhouse_active: ' + str(inhouse_active) + '\n' +
                           'inhouse_started: ' + str(inhouse_started) + '\n' +
                           'inhouse_ready: ' + str(inhouse_ready) + '\n' 
                           'inhouse_current: ' + str(inhouse_current) + '\n' +
                           'inhouse_total: ' + str(inhouse_total) + '\n' +
                           'inhouse_players: ' + str(player_list).strip('[]') + '\n' +
                           'inhouse_t1_slots: ' + str(inhouse_t1_slots) + '\n' +
                           'inhouse_t1: ' + str(player_t1_list).strip('[]') + '\n' +
                           'inhouse_t2_slots: ' + str(inhouse_t2_slots) + '\n' +
                           'inhouse_t2: ' + str(player_t2_list).strip('[]') + '\n' +
                           'inhouse_game: ' + str(inhouse_game))

def setup(bot):
    bot.add_cog(Inhouse(bot))