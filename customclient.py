from discord.ext.commands import Bot as DBot
import re as r


class CustomClient(DBot):

	def __init__(self, db, **options):
		super().__init__(**options)
		self.db = db
		self.del_time_small = 10
		self.del_time_mid = 30
		self.del_time_long = 60
		self.prefixes = dict()
	
	async def send(self, sendable, content):
		if len(content) <= 2000:
			await sendable.send(content)
			return
		contentlist = [""]
		k = 0
		s = ""
		for c in content:
			if c != " ":
				s += c
			else:
				if len(contentlist[k]) + len(s) <= 2000:
					contentlist[k] = contentlist[k] + " " + s
					s = ""
				else:
					k += 1
					contentlist.append(s)
					s = ""
		else:
			contentlist.append(s)
		for i in contentlist:
			await sendable.send(i)
	
	async def delete_cmd(self, ctx):
		if ctx.guild is None:
			return
		await ctx.channel.purge(limit=1)

	async def unverified(self):
		pass  # TODO

	async def verified(self):
		pass  # TODO

	def dbconf_get(self, guild_id, name, default=None):
		result = self.db.get(guild_id).execute("SELECT value FROM config WHERE name = ?", (name,)).fetchall()

		if len(result) < 1:
			return default

		return str(result[0][0])

	def dbconf_set(self, guild_id, name, value):
		saved = self.dbconf_get(guild_id, name)

		if saved is None:
			with self.db.get(guild_id) as db:
				db.execute("INSERT INTO config(name, value) VALUES(?, ?)", (name, value))
			return

		if str(saved) == str(value):
			return

		with self.db.get(guild_id) as db:
			db.execute("UPDATE config SET value = ? WHERE name = ?", (value, name))

	# OVERRIDE
	async def close(self):
		await super().close()
		self.db.close_all()
