import discord
from redbot.core import commands
from redbot.core import checks, commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import escape

def allowed_to_create():
	async def pred(ctx):
		if not ctx.guild:
			return False
		min_role_id = await ctx.cog.settings.guild(ctx.guild).min_role()
		if min_role_id == 0:
			min_role = ctx.guild.default_role
		else:
			min_role = discord.utils.get(ctx.guild.roles, id=min_role_id)
		if ctx.author == ctx.guild.owner:
			return True
		elif await ctx.bot.is_mod(ctx.author):
			return True
		elif ctx.author.top_role in sorted(ctx.guild.roles)[min_role.position :]:
			return True
		else:
			return False

	return commands.check(pred)


class Quotes(commands.Cog):
	"""A quote formatter and poster"""
	
	default_guild = {"quotes": [], "min_role": 0, "next_available_id": 1, "channel": 0}
	default_member = {"dms": False}

	def __init__(self, bot: Red):
		self.bot = bot
		self.settings = Config.get_conf(self, identifier=59595922, force_registration=True)
		self.settings.register_guild(**self.default_guild)
		self.settings.register_member(**self.default_member)

	@commands.group()
	@commands.guild_only()
	async def quote(self, ctx: commands.Context):
		"""Base command for quote creation tool.
		
		Use quoteset for settings"""
		pass

	@quote.command(name="create")
	@allowed_to_create()
	async def quote_create(self, member, ctx, *items):
		"""
		If a minimum required role has been set, users must have that role or
		higher, be in the mod/admin role, or be the guild owner in order to use this command
		
		The quote will only be created if all information is provided properly.
		Porper format is Double quotes surrounding quote followed by double quotes surrounding where its from/who its by
		"""
		items = [escape(c, mass_mentions=True) for c in items]
		if len(items) == 2:
			channel = member.guild.get_channel(await self.config.guild(member.guild).channel())
			if channel is None:
				channel = guild.system_channel
			content = items[0]
			byfrom = items[1]
			poster = ctx.author
			embed=discord.Embed(title=content, description=byfrom)
			embed.set_footer(text=poster)
			await ctx.send(embed=embed)
			await channel.send(embed=embed)
			
		else:
			await ctx.send("Not properly formatted. Porper format is double quotes surrounding quote followed by double quotes surrounding where its from/who its by")

	@commands.group()
	@checks.admin_or_permissions(manage_guild=True)
	@commands.guild_only()
	async def quoteset(self, ctx: commands.Context):
		"""quote maker settings"""
		pass

	@quoteset.command(name="role")
	@checks.admin_or_permissions(manage_guild=True)
	async def quoteset_role(self, ctx: commands.Context, *, role: discord.Role = None):
		"""Set the minimum role required to create quotes.
		Default is for everyone to be able to create quotes"""
		guild = ctx.guild
		if role is not None:
			await self.settings.guild(guild).min_role.set(role.id)
			await ctx.send("Role set to {}".format(role))
		else:
			await self.settings.guild(guild).min_role.set(0)
			await ctx.send("Role unset!")

	@quoteset.command(name="channel")
	@checks.admin_or_permissions(manage_guild=True)
	async def quoteset_channel(self, ctx: commands.Context, channel: discord.TextChannel):
		"""
		Sets the channel where quotes will be sent
		If this is not set, the channel will default to the channel used
		for new member messages (Server Settings > Overview > New Member
		Messages Channel on desktop). If that is set to `No new member messages`,
		the event start announcement will not be sent to a channel in the server
		and will only be sent directly to the participants via DM
		"""
		await self.settings.guild(ctx.guild).channel.set(channel.id)
		await ctx.tick()
