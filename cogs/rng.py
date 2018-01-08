from discord.ext import commands
import random

class RNG:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def coinflip(self):
        """ Flips a coin """
        bot_coin = random.choice(["heads", "tails"])
        await self.bot.say("The coin lands as **{0}**".format(bot_coin.upper()))

    @commands.command()
    async def rtd(self, min_number: int, max_number: int):
        """ Roll the Dice """
        try:
            dice_number = random.randint(min_number, max_number)
            await self.bot.say('You rolled ' + str(dice_number))
        except Exception as e:
            await self.bot.say('Invalid Input {0}'.format(e))

    @commands.command()
    async def ratewaifu(self, waifu: str):
        """ Rates a given waifu from 1-10 """
        rating = random.randint(0, 10)

        if (rating == 0):
            await self.bot.say("I rate your waifu: " + waifu + " a " + str(rating) + ". Serves you right for picking her BAKA!")
        elif (rating == 10):
            await self.bot.say("I rate your waifu: " + waifu + " a " + str(rating) + ". She.. isn't that good, b-b-BAKA!")
        elif (waifu == self.bot.user.name):
            await self.bot.say("I rate myself a 10! THE BEST, how dare you question me BAKA!")
        else:
            await self.bot.say("I rate your waifu: " + waifu + " a " + str(rating) + ".")

    @commands.command()
    async def choice(self, *options: str):
        """Makes a choice for the user"""
        await self.bot.say("I'd choose " + random.choice(options))

    @commands.command()
    async def rps(self, user_hand: str):
        """ Rock Paper Scissors
            Easter Egg: はさみ For User Scissors in JP """
        bot_choice = random.choice(["rock", "paper", "scissors"])

        if user_hand == "rock" or user_hand == "paper" or user_hand == "scissors" or user_hand == "はさみ":
            if bot_choice == user_hand:
                await self.bot.say("Its a tie. It isn't like you won or anything! BAKA")

            elif bot_choice == "rock" and user_hand == "paper":
                await self.bot.say("You win against " + self.bot.user.name + "'s Rock. It's not like I let you win or anything BAKA!")
            elif bot_choice == "rock" and user_hand == "scissors":
                await self.bot.say("You lose against " + self.bot.user.name + "'s Rock")

            elif bot_choice == "paper" and user_hand == "rock":
                await self.bot.say("You lose against " + self.bot.user.name + "'s Paper")
            elif bot_choice == "paper" and user_hand == "scissors":
                await self.bot.say(
                    "You win against " + self.bot.user.name + "'s Paper. It's not like I let you win or anything BAKA!")

            elif bot_choice == "scissors" and user_hand == "rock":
                await self.bot.say(
                    "You win against " + self.bot.user.name + "'s Scissors. It's not like I let you win or anything BAKA!")

            elif bot_choice == "paper" and user_hand == "はさみ":
                await self.bot.say("You win against " + self.bot.user.name + "'s Paper baka weeb")
            elif bot_choice == "rock" and user_hand == "はさみ":
                await self.bot.say("You lose against " + self.bot.user.name + "'s Rock baka weeb")

            else:
                await self.bot.say("You lose against " + self.bot.user.name + "'s Scissors")
        else:
            await self.bot.say('Invalid input, I want rock, paper or scissors! BAKA')

def setup(bot):
    bot.add_cog(RNG(bot))