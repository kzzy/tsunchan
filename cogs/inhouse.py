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
t1_captain = None # Team 1 Captain in Captain's Mode
t2_captain = None # Team 2 Captain in Captain's Mode
inhouse_t1 = []  # List for Team 1 players
inhouse_t2 = []  # List for Team 2 players
inhouse_t1_slots = 0  # Team 1 total slots
inhouse_t2_slots = 0  # Team 2 total slots
inhouse_channels = {'Lobby' : '395892786999721986',       # Lobby     ID
                    'Channel 1' : '395897418094215168',   # Channel 1 ID
                    'Channel 2' : '395897458032377859',   # Channel 2 ID
                    'Inhouse Text' : '396568588934447105', # Text Channel ID
                    'Debug' : '401729963704975362'
                    }
inhouse_cpt_screen = "" # Text print for cpt mode picking phase
inhouse_cpt_ttp = None  # Captain's turn to pick
inhouse_picking = False # Boolean used to check if Picking phase is in progress
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
                    if player_t1 is t1_captain and player_t2 is t2_captain:
                        txt += "`(CPT) {:<29}(CPT) {}`".format(player_t1.display_name, player_t2.display_name)
                    else:
                        txt += "`{:<35}{}`".format(player_t1.display_name, player_t2.display_name)
                txt += '\n'

        elif instruct == "teams_cpt":
            txt = ""
            txt += '```{0}\'s Turn to Pick```\n'.format(input_1)
            txt += self.print_ih("teams")
            txt += '\n\n'
            player_list = "\n".join([str(x.display_name) for x in inhouse_players])
            txt += player_list

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
            txt += "There were no names found with your search."

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
        elif instruct == "cpt_too_many_args":
            txt += '```Too many args were given for captains mode\nLeave it blank for Random Captains, otherwise specify the Names\n\n'
            txt += 'Run the !start command again```'

        elif instruct == "not_a_cpt":
            txt += 'You are not a captain in this round.'

        elif instruct == "no_picking":
            txt += 'Picking phase is not active.'

        elif instruct == 'not_cpt_turn':
            txt += 'It is not your turn to pick.'

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
                mode = "Standard"
            elif inhouse_mode == 'captains':
                # Slot checking for ONLY 5 VS 5
                if int(t1_slots) != 5 and int(t2_slots) != 5:
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
        inhouse_t1_slots = int(t1_slots)
        inhouse_t2_slots = int(t2_slots)
        inhouse_total = int(t1_slots) + int(t2_slots)

        await self.bot.say(self.print_ih('init_inhouse', member.display_name, inhouse_game, mode, t1_slots, t2_slots))

    async def standard_setup(self):
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

        # Sort alphabetically
        inhouse_t1.sort(key=lambda x: x.display_name)
        inhouse_t2.sort(key=lambda x: x.display_name)

        await self.bot.say(self.print_ih("ready_help") + '\n' + self.print_ih("teams"))

    async def captains_setup(self, captains):
        global inhouse_started
        global t1_captain
        global t2_captain

        # Randomize order of captains
        captains = list(captains)
        random_pick = random.choice(captains)

        """ Handle setup for CAPTAINS mode"""
        # Manual Captain Picking
        if len(captains) > 0:
            t1_captain = self.search_player(random_pick, inhouse_players)
            captains.remove(random_pick)    # Remove as there are two players remaining

            # Check for any error codes returned
            if (t1_captain == -1):
                await self.bot.say(self.print_ih('too_many_cases'))
                return
            elif (t1_captain == 0):
                await self.bot.say(self.print_ih('not_found'))
                return

            t2_captain = self.search_player(captains.pop(), inhouse_players) # Pop as there is only one player remaining
            if (t2_captain == -1):
                await self.bot.say(self.print_ih('too_many_cases'))
                return
            elif (t2_captain == 0):
                await self.bot.say(self.print_ih('not_found'))
                return

            # Move the captains to their respective team fields
            inhouse_t1.append(inhouse_players.pop(inhouse_players.index(t1_captain)))
            inhouse_t2.append(inhouse_players.pop(inhouse_players.index(t2_captain)))

        # Random Captains
        else:
            t1_captain = random.choice(inhouse_players)
            inhouse_t1.append(inhouse_players.pop(inhouse_players.index(t1_captain)))
            t2_captain = random.choice(inhouse_players)
            inhouse_t2.append(inhouse_players.pop(inhouse_players.index(t2_captain)))

        # Move Captains into their voice channel first
        await self.bot.move_member(t1_captain, self.bot.get_channel(inhouse_channels.get("Channel 1")))
        await self.bot.move_member(t2_captain, self.bot.get_channel(inhouse_channels.get("Channel 2")))

        global inhouse_cpt_screen
        global inhouse_picking
        inhouse_started = True
        inhouse_picking = True

        # Captains on team already
        txt = self.print_ih('teams_cpt', t1_captain.display_name)
        inhouse_cpt_screen = await self.bot.send_message(self.bot.get_channel(inhouse_channels.get("Inhouse Text")), txt)
        await self.pick_order()

    async def pick_order(self):
        """ Function to control captain's mode pick order"""
        """1-2-2-1-1"""
        global inhouse_cpt_ttp

        # Start
        if len(inhouse_t1) == 1 and len(inhouse_t2) == 1:
            inhouse_cpt_ttp = t1_captain

        # Team 1 Picked 1
        if len(inhouse_t1) == 2 and len(inhouse_t2) == 1:
            txt = self.print_ih('teams_cpt', t2_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)
            inhouse_cpt_ttp = t2_captain

        # Team 2 Pick 1
        if len(inhouse_t1) == 2 and len(inhouse_t2) == 2:
            txt = self.print_ih('teams_cpt', t2_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)

        # Team 2 Pick 1
        if len(inhouse_t1) == 2 and len(inhouse_t2) == 3:
            txt = self.print_ih('teams_cpt', t1_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)
            inhouse_cpt_ttp = t1_captain

        # Team 1 Pick 1
        if len(inhouse_t1) == 3 and len(inhouse_t2) == 3:
            txt = self.print_ih('teams_cpt', t1_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)

        # Team 1 Pick 1
        if len(inhouse_t1) == 4 and len(inhouse_t2) == 3:
            txt = self.print_ih('teams_cpt', t2_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)
            inhouse_cpt_ttp = t2_captain

        # Team 2 Picked 1
        if len(inhouse_t1) == 4 and len(inhouse_t2) == 4:
            txt = self.print_ih('teams_cpt', t1_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)
            inhouse_cpt_ttp = t1_captain

        # Team 1 Picked 1
        if len(inhouse_t1) == 5 and len(inhouse_t2) == 4:
            txt = self.print_ih('teams_cpt', t2_captain.display_name)
            await self.bot.edit_message(inhouse_cpt_screen, txt)

        # Team 2 Picked 1
        if len(inhouse_t1) == 5 and len(inhouse_t2) == 5:
            txt = '```Final Teams!```\n'
            txt += self.print_ih('teams')
            await self.bot.edit_message(inhouse_cpt_screen, self.print_ih('teams'))
            inhouse_cpt_ttp = None

    @inhouse.command(pass_context=True, aliases=['p'])
    async def pick(self, ctx, player: str):
        """Pick for Captain's Mode"""
        global inhouse_picking
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

        # Check if there is no inhouse in-progress
        if inhouse_started is False:
            await self.bot.say(self.print_ih('no_inprogress_inhouse'))
            return

        # Check if its picking phase
        if inhouse_picking is False:
            await self.bot.say(self.print_ih('no_picking'))
            return

        # Check if author is a captain
        if member is not t1_captain and member is not t2_captain:
            await self.bot.say(self.print_ih('not_a_cpt'))
            return

        # Not this specific captain's turn to pick
        if member is not inhouse_cpt_ttp:
            await self.bot.say(self.print_ih('not_cpt_turn'))
            return

        await self.bot.delete_message(ctx.message) # Delete pick msg to avoid clutter after checks

        # Pick players and move them into the voice channels automatically
        if member is t1_captain:
            player = self.search_player(player, inhouse_players)
            # Check for any error codes returned
            if (player == -1):
                await self.bot.say(self.print_ih('too_many_cases'))
                return
            elif (player == 0):
                await self.bot.say(self.print_ih('not_found'))
                return
            inhouse_t1.append(inhouse_players.pop(inhouse_players.index(player)))
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 1")))
        else:
            player = self.search_player(player, inhouse_players)
            # Check for any error codes returned
            if (player == -1):
                await self.bot.say(self.print_ih('too_many_cases'))
                return
            elif (player == 0):
                await self.bot.say(self.print_ih('not_found'))
                return
            inhouse_t2.append(inhouse_players.pop(inhouse_players.index(player)))
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 2")))

        # Check if only one player remains after pick and auto move to team missing the player
        # Also moves them into voice channel
        if len(inhouse_t1) == inhouse_t1_slots:
            player = inhouse_players.pop()
            inhouse_t2.append(player)
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 2")))

            # Turn off picking
            inhouse_picking = False

        elif len(inhouse_t2) == inhouse_t2_slots:
            player = inhouse_players.pop()
            inhouse_t1.append(player)
            await self.bot.move_member(player, self.bot.get_channel(inhouse_channels.get("Channel 1")))

            # Turn off picking
            inhouse_picking = False

        # Evaluate pick order
        await self.pick_order()

    @inhouse.command(pass_context=True)
    async def start(self, ctx, *args):
        """Starts an inhouse"""
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

        if inhouse_modes.get('captains') is True:
            # inhouse_started will be set once further checks in captains_setup are fulfilled
            # No args = Random Captains | MAX 2 args = 1 Captain per team
            if len(args) > 2:
                await self.bot.say(self.print_ih('cpt_too_many_args'))
                return
            await self.captains_setup(args) # Pass args to the captains_setup func
        else:
            # Default
            inhouse_started = True
            await self.standard_setup()

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

    @inhouse.command(aliases=['fk'], hidden=True)
    async def db(self):
        """ Debugger to just randomly move ppl into inhouse_players to test other funcs"""
        global inhouse_current
        global inhouse_total
        everybody = []
        for x in self.bot.get_all_members():
            everybody.append(x)

        txt = ""
        guy = ""
        while(inhouse_current != inhouse_total):
            guy = everybody.pop()
            txt += "{0}\n".format(guy.display_name)
            inhouse_players.append(guy)
            inhouse_current += 1

        global inhouse_ready
        inhouse_ready = True
        await self.bot.say('**__Added__**\n' + txt)

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
        if member in inhouse_players:
            await self.bot.say(self.print_ih('already_in_queue', member.display_name))
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
        if player is not None:
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
        global t1_captain
        global t2_captain
        global inhouse_picking

        # Role Check
        member = ctx.message.author  # Fetch author user and permissions
        if self.check_role(member, "Inhouse") is False:
            return

        if inhouse_active is True:
            # Reset variables
            inhouse_modes.update({"standard": False})
            inhouse_modes.update({"captains": False})
            t1_captain = None
            t2_captain = None
            inhouse_active = False
            inhouse_started = False
            inhouse_ready = False
            inhouse_picking = False
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