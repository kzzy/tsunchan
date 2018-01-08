import asyncio
import discord
import random

class Auto:
    def __init__(self, bot):
        self.bot = bot

    async def pick_status(self):
        """Randomly generates a new status on duration"""
        while self.bot.is_logged_in:
            status = random.choice(["with Rem",
                                    "with Ram",
                                    "with Emilia",
                                    "with Noumi Kudryavka",
                                    "with Illya",
                                    "with Chitoge",
                                    "with Yoshino",
                                    "with Arisu Shimada",
                                    "with Shirokuma",
                                    "with Karen",
                                    "with Kyon's Sister",
                                    "with Est",
                                    "with Aria Kanzaki",
                                    "with the Nep Sisters",
                                    "with Chino",
                                    "with Kyouko",
                                    "with Konata",
                                    "with Enju",
                                    "with Kirin Toudou",
                                    "with Shinobu",
                                    "with Megumin",
                                    "with Mikan",
                                    "with kazu",  # yaya no
                                    "with Indekkusu"])
            await self.bot.change_presence(game=discord.Game(name=status, type=1), status=discord.Status.online)
            await asyncio.sleep(12)  # loops every 12 seconds

    def check_ping(ip):
        avg_ping = 0.0
        ping_command = "ping -n -c 5 -W 3 " + ip

        (output, error) = subprocess.Popen(ping_command,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           shell=True).communicate()

        # Regex to parse the decoded byte input into string
        pattern = r'time=([0-9]+(\.[0-9]+)*)'
        pings = re.findall(pattern, output.decode('utf=8'))

        # Calculate Average ping
        for ping in pings:
            avg_ping += float(ping[0])
        avg_ping = avg_ping / 5

        return avg_ping

    async def ping():
        region_dict = {}
        region_dict['us-west'] = 0.0
        region_dict['us-central'] = 0.0
        region_dict['us-east'] = 0.0

        # Default Server Location : us-west
        current_region = "us-west"
        id = "131339092830060544"  # The Crew server id MUST BE STRING FORMAT
        server = bot.get_server(id)
        # await bot.edit_server(server, region=discord.ServerRegion(current_region))

        while bot.is_logged_in:
            avg_west = check_ping("45.35.39.162")  # WEST 144
            avg_central = check_ping("104.200.145.226")  # CENTRAL 165
            avg_east = check_ping("138.128.21.106")  # EAST 119

            # Update existing ping values
            region_dict['us-west'] = avg_west
            region_dict['us-central'] = avg_central
            region_dict['us-east'] = avg_east

            # Print to log file
            logger.info("Current West Average:{0}".format(avg_west))
            logger.info("Current Central Average:{0}".format(avg_central))
            logger.info("Current East Average:{0}".format(avg_east))

            # Determine region with lowest ping and change server region if it does not match the current region
            min_region = min(region_dict.items(), key=lambda x: x[1])[0]
            if min_region != current_region:
                logger.info("Region changed from {0} to {1}".format(current_region, min_region))
                await bot.edit_server(server, region=discord.ServerRegion(min_region))
            await asyncio.sleep(30)  # loops every 30 seconds

def setup(bot):
    bot.add_cog(Auto(bot))