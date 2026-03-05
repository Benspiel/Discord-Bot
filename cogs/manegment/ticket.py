import discord
from discord.ext import commands

# Panel-Channel
TICKET_PANEL_CHANNEL = 1439619315409227787

# Kategorien
CATEGORY_GENERAL = 1439621132641894471
CATEGORY_TECH = 1442455936772870154
CATEGORY_APPLY = 1442455846809374771

# Logging Channel
LOG_CHANNEL = 1439618086943592549

# Support Rolle (Ping & Permissions)
SUPPORT_ROLE_ID = 1439600362511401050


# ---------------------------------------------------------
# TICKET NUMBER
# ---------------------------------------------------------

async def get_next_ticket_number(guild: discord.Guild):
    count = 0
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and "ticket-" in channel.name:
            count += 1
    return f"{count + 1:04d}"


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

async def log_ticket_action(guild, user: discord.User, ticket_number, action, color):
    log_channel = guild.get_channel(LOG_CHANNEL)
    if not log_channel:
        return

    embed = discord.Embed(title="Logged Info", color=color)
    embed.set_author(
        name=f"{user.name}",
        icon_url=user.avatar.url if user.avatar else user.default_avatar.url
    )
    embed.add_field(name="Ticket:", value=f"Ticket-{ticket_number}", inline=False)
    embed.add_field(name="Action:", value=action, inline=False)

    await log_channel.send(embed=embed)


# ---------------------------------------------------------
# CLOSE BUTTON
# ---------------------------------------------------------

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticket schließen",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="ticket_close_button"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            ticket_number = interaction.channel.name.split("-")[-1]
        except:
            ticket_number = "0000"

        await log_ticket_action(
            interaction.guild,
            interaction.user,
            ticket_number,
            "Closed",
            discord.Color.red()
        )

        await interaction.response.send_message("🔒 Ticket wird geschlossen...", ephemeral=True)
        await interaction.channel.delete(reason="Ticket geschlossen")


# ---------------------------------------------------------
# TICKET CHANNEL ERSTELLEN (MIT PERMISSIONS)
# ---------------------------------------------------------

async def create_ticket_channel(interaction: discord.Interaction, ticket_type: str, category_id: int):
    guild = interaction.guild
    user = interaction.user
    support_role = guild.get_role(SUPPORT_ROLE_ID)

    ticket_number = await get_next_ticket_number(guild)
    channel_name = f"ticket-{ticket_type}-{ticket_number}"

    # Berechtigungen setzen
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Support-Rolle zu den Berechtigungen hinzufügen
    if support_role:
        overwrites[support_role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            manage_messages=True  # Optional: Team darf Nachrichten löschen
        )

    category = guild.get_channel(category_id)

    # Channel erstellen
    channel = await guild.create_text_channel(
        name=channel_name,
        overwrites=overwrites,
        category=category
    )

    # Support-Rolle pingen
    if support_role:
        await channel.send(f"{support_role.mention} - Neues Ticket von {user.mention}")
    else:
        await channel.send(f"Info: Support-Rolle mit ID {SUPPORT_ROLE_ID} wurde nicht gefunden!")

    # Logging: Created
    await log_ticket_action(guild, user, ticket_number, "Created", discord.Color.green())

    return channel, ticket_number


# ---------------------------------------------------------
# MODALS
# ---------------------------------------------------------

class NormalTicketModal(discord.ui.Modal, title="📩 Normales Ticket"):
    anliegen = discord.ui.TextInput(label="Was ist dein Anliegen?", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        channel, ticket_number = await create_ticket_channel(interaction, "normal", CATEGORY_GENERAL)
        embed = discord.Embed(
            title=f"📩 Ticket-{ticket_number}",
            description=f"**User:** {interaction.user.mention}\n\n**Anliegen:**\n{self.anliegen.value}",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message("✅ Ticket erstellt!", ephemeral=True)


class TechSupportModal(discord.ui.Modal, title="🛠️ Technischer Support"):
    hilfe = discord.ui.TextInput(label="Wobei brauchst du Hilfe?", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        channel, ticket_number = await create_ticket_channel(interaction, "tech", CATEGORY_TECH)
        embed = discord.Embed(
            title=f"🛠️ Ticket-{ticket_number}",
            description=f"**User:** {interaction.user.mention}\n\n**Problem:**\n{self.hilfe.value}",
            color=discord.Color.orange()
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message("✅ Support-Ticket erstellt!", ephemeral=True)


class BewerbungModal(discord.ui.Modal, title="📄 Bewerbung"):
    bewerbung = discord.ui.TextInput(label="Warum möchtest du dich bewerben?", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        channel, ticket_number = await create_ticket_channel(interaction, "bewerbung", CATEGORY_APPLY)
        embed = discord.Embed(
            title=f"📄 Bewerbung-{ticket_number}",
            description=f"**Bewerber:** {interaction.user.mention}\n\n**Text:**\n{self.bewerbung.value}",
            color=discord.Color.green()
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message("✅ Bewerbung gesendet!", ephemeral=True)


# ---------------------------------------------------------
# DROPDOWN & VIEW
# ---------------------------------------------------------

class TicketSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Wähle eine Ticket-Art...",
            custom_id="ticket_dropdown",
            options=[
                discord.SelectOption(label="Normal", emoji="📩"),
                discord.SelectOption(label="Technischer Support", emoji="🛠️"),
                discord.SelectOption(label="Bewerbung", emoji="📄"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Normal":
            await interaction.response.send_modal(NormalTicketModal())
        elif self.values[0] == "Technischer Support":
            await interaction.response.send_modal(TechSupportModal())
        elif self.values[0] == "Bewerbung":
            await interaction.response.send_modal(BewerbungModal())


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ---------------------------------------------------------
# COG
# ---------------------------------------------------------

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Persistente Views registrieren
        bot.add_view(TicketView())
        bot.add_view(CloseTicketView())

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(TICKET_PANEL_CHANNEL)
        if channel:
            await channel.purge(limit=10)
            embed = discord.Embed(
                title="🎫 Ticketsystem",
                description="Wähle unten eine Ticket-Art aus, um Hilfe zu erhalten oder dich zu bewerben.",
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, view=TicketView())
        print(f"Ticket-System bereit als {self.bot.user}")


async def setup(bot):
    await bot.add_cog(TicketCog(bot))