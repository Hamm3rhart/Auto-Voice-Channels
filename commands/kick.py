import cfg
import discord
import utils
import functions as func
from math import floor
from commands.base import Cmd
from time import time

help_text = [
    [
        ("Usage:",
         "```<PREFIX><COMMAND> @USER```"
         "```<PREFIX><COMMAND> @USER\nREASON```"),
        ("Description:",
         "Initiate a votekick to remove a user from your channel and prevent them from joining again. "
         "**More than half** of the remaining users must vote yes in order for the member to be kicked.\n\n"
         "If you wish to allow a kicked user to return to the channel, you will all have to leave and create a new "
         "channel instead, or if you are a server admin, manually edit the channel permissions.\n\n"
         "The person who initially created the channel cannot be kicked (unless they leave voluntarily and later "
         "return, in which case the \"creator\" of the channel is reassigned to the person who was at the top of the "
         "channel when they left.)"),
        ("Examples:",
         "```<PREFIX><COMMAND> @pixaal```"
         "```<PREFIX><COMMAND> pixaal#1234\nBeing mean :(```"
         "```<PREFIX><COMMAND> pixaal\nSound board abuse```"),
    ]
]


async def execute(ctx, params):
    params_str = ' '.join(params).strip()
    guild = ctx['guild']
    settings = ctx['settings']
    author = ctx['message'].author
    vc = ctx['voice_channel']
    parts = params_str.split('\n', 1)
    name = parts[0]
    reason = parts[1] if len(parts) > 1 else None

    user = utils.get_user_in_channel(name, vc)

    if not user:
        return False, "Du kannst nur Nutzer aus deiner momentanen Crew (\"{}\") kicken.".format(name)
    if user.id == utils.get_creator_id(settings, vc):
        return False, "Du kannst den Ersteller der Crew nicht kicken."
    if user == author:
        return False, "Bitte kick dich nicht selber :frowning:"

    participants = [m for m in vc.members if m not in [author, user] and not m.bot]
    required_votes = floor((len(participants) + 1) / 2) + 1
    try:
        text = (
            "‼ **Votekick** ‼\n"
            "{initiator} startet einen Votekick gegen {offender}.{reason}\n\n"
            "{participants}:\nReagiere mit ✅ um für **Ja** zu stimmen, {offender} zu kicken, "
            "oder ignoriere diese Nachricht um für **Nein** zu stimmen.\n\n"
            "Du hast **2 Minuten** Zeit um abzustimmen. Für eine Erfolgreiche abstimmung ist eine Ratio von {req} zu {tot} notwendig.\n"
            "{initiator} deine Stimme wurde automatisch gezählt. Es werden nur die Stimmen der Anwesenden in der Crew gewertet."
            "".format(
                initiator=author.mention,
                offender=user.mention,
                reason=(" Begründung: **{}**".format(reason) if reason else ""),
                participants=' '.join([m.mention for m in participants]),
                req=required_votes,
                tot=len(participants) + 1
            )
        )
        if not participants:
            text = "..."
        m = await ctx['message'].channel.send(text)
    except discord.errors.Forbidden:
        return False, "I don't have permission to reply to your kick command."
    cfg.VOTEKICKS[m.id] = {
        "initiator": author,
        "participants": participants,
        "required_votes": required_votes,
        "offender": user,
        "reason": reason,
        "in_favor": [author],
        "voice_channel": vc,
        "message": m,
        "end_time": time() + 120
    }
    try:
        if participants:
            await m.add_reaction('✅')
    except discord.errors.Forbidden:
        pass
    await func.server_log(
        guild,
        "👢 {} (`{}`) initiated a votekick against **{}** (`{}`) in \"**{}**\". Reason: *{}*.".format(
            func.user_hash(author), author.id, func.user_hash(user), user.id, vc.name, reason
        ), 1, settings)
    return True, "NO RESPONSE"


command = Cmd(
    execute=execute,
    help_text=help_text,
    params_required=1,
    admin_required=False,
    voice_required=True,
)
