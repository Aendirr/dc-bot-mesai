import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, GUILD_ID, LOG_CHANNEL_ID
from store import store
from utils import utc_now, to_iso, from_iso, seconds_to_text


intents = discord.Intents.default()
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


async def send_log(guild: discord.Guild | None, embed: discord.Embed) -> None:
    if guild is None:
        return

    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        return

    if isinstance(channel, discord.TextChannel):
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass


class MesaiView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Mesai Gir",
        style=discord.ButtonStyle.success,
        custom_id="mesai_gir_button"
    )
    async def mesai_gir(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        ok, message = await store.start_shift(interaction.user)

        embed = discord.Embed(
            title="Mesai Sistemi",
            description=message,
            color=discord.Color.green() if ok else discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        if ok:
            log_embed = discord.Embed(
                title="Mesai Giriş",
                color=discord.Color.green()
            )
            log_embed.add_field(name="Kullanıcı", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="ID", value=f"`{interaction.user.id}`", inline=True)
            log_embed.add_field(name="Zaman", value=f"`{to_iso(utc_now())}`", inline=True)
            await send_log(interaction.guild, log_embed)

    @discord.ui.button(
        label="Mesaiden Çık",
        style=discord.ButtonStyle.danger,
        custom_id="mesaiden_cik_button"
    )
    async def mesaiden_cik(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        ok, message, worked_seconds = await store.end_shift(interaction.user)

        if ok:
            user_data = await store.get_user(interaction.user.id)
            total_seconds = int(user_data.get("total_seconds", 0)) if user_data else 0
            message = (
                f"Mesaiden çıktın.\n"
                f"Bu oturum: `{seconds_to_text(worked_seconds)}`\n"
                f"Toplam: `{seconds_to_text(total_seconds)}`"
            )

        embed = discord.Embed(
            title="Mesai Sistemi",
            description=message,
            color=discord.Color.red() if ok else discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        if ok:
            log_embed = discord.Embed(
                title="Mesai Çıkış",
                color=discord.Color.red()
            )
            log_embed.add_field(name="Kullanıcı", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="ID", value=f"`{interaction.user.id}`", inline=True)
            log_embed.add_field(name="Oturum", value=f"`{seconds_to_text(worked_seconds)}`", inline=True)
            log_embed.add_field(name="Zaman", value=f"`{to_iso(utc_now())}`", inline=False)
            await send_log(interaction.guild, log_embed)


@bot.event
async def on_ready() -> None:
    bot.add_view(MesaiView())

    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Giriş yapıldı: {bot.user}")
        print(f"Slash komut sayısı: {len(synced)}")
    except Exception as error:
        print(f"Sync hatası: {error}")


@bot.tree.command(
    name="panel",
    description="Mesai panelini gönderir",
    guild=discord.Object(id=GUILD_ID)
)
async def panel(interaction: discord.Interaction) -> None:
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "Bu komut için `Sunucuyu Yönet` yetkin olmalı.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Mesai Kontrol Paneli",
        description="Aşağıdaki butonlarla mesai giriş ve çıkış yapabilirsin.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Butonlar", value="`Mesai Gir` • `Mesaiden Çık`", inline=False)
    embed.add_field(name="Komutlar", value="`/durum` • `/liste` • `/bak`", inline=False)

    await interaction.response.send_message(embed=embed, view=MesaiView())


@bot.tree.command(
    name="durum",
    description="Kendi mesai bilgini gösterir",
    guild=discord.Object(id=GUILD_ID)
)
async def durum(interaction: discord.Interaction) -> None:
    user_data = await store.get_user(interaction.user.id)

    if not user_data:
        await interaction.response.send_message("Henüz kaydın yok.", ephemeral=True)
        return

    total_seconds = int(user_data.get("total_seconds", 0))
    today_seconds = await store.get_period_seconds(interaction.user.id, 1)
    week_seconds = await store.get_period_seconds(interaction.user.id, 7)
    active = bool(user_data.get("active"))
    started_at = from_iso(user_data.get("started_at"))

    lines = [
        f"**Kullanıcı:** {interaction.user.mention}",
        f"**ID:** `{interaction.user.id}`",
        f"**Durum:** `{'Aktif' if active else 'Pasif'}`",
        f"**Bugün:** `{seconds_to_text(today_seconds)}`",
        f"**Son 7 Gün:** `{seconds_to_text(week_seconds)}`",
        f"**Toplam:** `{seconds_to_text(total_seconds)}`"
    ]

    if active and started_at:
        live_seconds = max(0, int((utc_now() - started_at).total_seconds()))
        lines.append(f"**Anlık Oturum:** `{seconds_to_text(live_seconds)}`")
        lines.append(f"**Başlangıç:** `{to_iso(started_at)}`")

    embed = discord.Embed(
        title="Mesai Durumu",
        description="\n".join(lines),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="liste",
    description="Toplam mesai sıralamasını gösterir",
    guild=discord.Object(id=GUILD_ID)
)
async def liste(interaction: discord.Interaction) -> None:
    top_users = await store.get_top_users(10)

    if not top_users:
        await interaction.response.send_message("Henüz kayıt yok.")
        return

    lines = []
    for index, item in enumerate(top_users, start=1):
        username = item.get("username", "Bilinmiyor")
        total_seconds = int(item.get("total_seconds", 0))
        active = bool(item.get("active"))
        suffix = " • `Aktif`" if active else ""
        lines.append(f"**{index}.** {username} - `{seconds_to_text(total_seconds)}`{suffix}")

    embed = discord.Embed(
        title="Mesai Sıralaması",
        description="\n".join(lines),
        color=discord.Color.gold()
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="bak",
    description="Bir kullanıcının mesaisine bakar",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(kullanici="Bakılacak kullanıcı")
async def bak(interaction: discord.Interaction, kullanici: discord.Member) -> None:
    user_data = await store.get_user(kullanici.id)

    if not user_data:
        await interaction.response.send_message("Bu kullanıcı için kayıt bulunamadı.")
        return

    total_seconds = int(user_data.get("total_seconds", 0))
    today_seconds = await store.get_period_seconds(kullanici.id, 1)
    week_seconds = await store.get_period_seconds(kullanici.id, 7)
    active = bool(user_data.get("active"))
    started_at = from_iso(user_data.get("started_at"))

    lines = [
        f"**Kullanıcı:** {kullanici.mention}",
        f"**ID:** `{kullanici.id}`",
        f"**Durum:** `{'Aktif' if active else 'Pasif'}`",
        f"**Bugün:** `{seconds_to_text(today_seconds)}`",
        f"**Son 7 Gün:** `{seconds_to_text(week_seconds)}`",
        f"**Toplam:** `{seconds_to_text(total_seconds)}`"
    ]

    if active and started_at:
        live_seconds = max(0, int((utc_now() - started_at).total_seconds()))
        lines.append(f"**Anlık Oturum:** `{seconds_to_text(live_seconds)}`")
        lines.append(f"**Başlangıç:** `{to_iso(started_at)}`")

    embed = discord.Embed(
        title="Mesai Bilgisi",
        description="\n".join(lines),
        color=discord.Color.teal()
    )

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)