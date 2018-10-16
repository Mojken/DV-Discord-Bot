import discord, json
import asyncio, time, datetime
import facebook

TOKEN = ''
FIELDS = 'type,message,story,link,created_time,full_picture,name'
GROUP_ID = 0
API_KEY = ''
CHANNEL = {}

json_data = {}

client = discord.Client()

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	command = getCommand(message)
	if command == "-1":
		return

	print("<- %s" % command)
	
	if command.startswith('help'):
		embed = discord.Embed(title="Help", colour=discord.Colour(0xE57A07), description="")
		embed.add_field(name=":DV: help", value="Display this message", inline=False)
		embed.add_field(name=":DV: set channel", value="Sets the channel to push the Facebook feed onto. Using more than once will probably break everything.", inline=False)

		await client.send_message(destination=message.channel, embed=embed)
		await client.delete_message(message)

	if command.startswith('set channel'):
		global CHANNEL
		CHANNEL = message.channel

		await send("Channel set", message)
		await client.delete_message(message)

		while True:
			await postLatestPost()
			await asyncio.sleep(144)


async def send(msg, message):
	print("-> %s" % msg.format(message))
	return await client.send_message(message.channel, msg.format(message))


def getCommand(message):
	command = message.content

	if command.startswith(':DV:'):
		command = command[4:]

	elif command.startswith('<:DV:'):
		command = command[command.find('>')+1:]

	else:
		return "-1"

	return command.strip()


async def postLatestPost():
	limit = json_data["timestamp"]
	
	data = api.get_connections(GROUP_ID, "feed", fields=FIELDS, since=limit)["data"]
	
	if not CHANNEL:
		return
	if len(data) == 0:
		return

	for post in data[::-1]:
		embed = createEmbedFromPost(post)
		await client.send_message(destination=CHANNEL, embed=embed)
	
	save("timestamp", addSecond(data[0]["created_time"]))


def parseDate(timestamp):
	time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
	return time.astimezone().strftime("%A %d %B at %H:%M")


def addSecond(timestamp):
	time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(seconds=1)
	return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def save(var, data):
	json_data[var] = data
	with open('DVD.json', 'w') as outfile:
		json.dump(json_data, outfile)


def createEmbedFromPost(post):
	post_type = post["type"]
	
	if post_type == "link":
		embed = discord.Embed(title=post["story"], colour=discord.Colour(0xE57A07), description=parseDate(post["created_time"]))
		if "message" in post:
			embed.add_field(name="Status", value=post["message"], inline=False)
		if "name" in post:
			embed.add_field(name=post["name"], value=post["link"], inline=True)
		if "full_picture" in post:
			embed.set_image(url=post["full_picture"])
	
	elif post_type == "status":
		embed = discord.Embed(title=post_type.capitalize(), colour=discord.Colour(0xE57A07), description=parseDate(post["created_time"]))
		if "message" in post:
			embed.add_field(name="Message", value=post["message"], inline=False)
	
	elif post_type == "photo":
		if "story" in post:
			embed = discord.Embed(title=post["story"], colour=discord.Colour(0xE57A07), description=parseDate(post["created_time"]))
		else:
			embed = discord.Embed(title=post_type.capitalize(), colour=discord.Colour(0xE57A07), description=parseDate(post["created_time"]))
		if "message" in post:
			embed.add_field(name="Message", value=post["message"], inline=False)
		if "full_picture" in post:
			embed.set_image(url=post["full_picture"])
	
	else:
		embed = discord.Embed(title="Unsupported post type", colour=discord.Colour(0xE57A07), description="Please yell at <@!104286743737405440> for not supporting %ss yet" % post_type)
	
	return embed


@client.event
async def on_ready():	
	print('DAA-TAVEE-TARE!')

with open('DVD.json', 'r') as infile:
		json_data = json.load(infile)
		TOKEN = json_data["token"]
		API_KEY = json_data["api_key"]
		GROUP_ID = json_data["group_id"]

api = facebook.GraphAPI(API_KEY)
client.run(TOKEN)
