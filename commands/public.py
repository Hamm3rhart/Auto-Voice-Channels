import cfg
import discord
import utils
from commands.base import Cmd

help_text = [
    [
        ("Usage:", "<PREFIX><COMMAND>"),
        ("Description:",
         "Make your private channel public again, so anyone can join."),
    ]
]


async def execute(ctx, params):
    guild = ctx['guild']
    settings = ctx['settings']
    vc = ctx['voice_channel']

    for p, pv in settings['auto_channels'].items():
        for s, sv in pv['secondaries'].items():
            if s == vc.id:
                if 'priv' not in sv or not sv['priv']:
                    return False, ("Deine Crew ist schon öffentlich. "
                                   "Schreibe `{}private` um sie privat zu machen.".format(ctx['print_prefix']))
                try:
                    await vc.set_permissions(guild.default_role, connect=True)
                except discord.errors.Forbidden:
                    return False, ("I don't have permission to do that."
                                   "Please make sure I have the *Manage Roles* permission in this server and category.")
                settings['auto_channels'][p]['secondaries'][s]['priv'] = False
                try:
                    jcid = settings['auto_channels'][p]['secondaries'][s]['jc']
                    del settings['auto_channels'][p]['secondaries'][s]['jc']
                except KeyError:
                    jcid = 0
                utils.set_serv_settings(guild, settings)
                if s in cfg.PRIV_CHANNELS:
                    del cfg.PRIV_CHANNELS[s]
                try:
                    jc = guild.get_channel(jcid)
                    if jc:
                        await jc.delete()
                except discord.errors.Forbidden:
                    return False, "Deine Crew ist wieder öffentlich, aber ich kann deinen **⇩ Join** Kanal nicht löschen :/."
                return True, "Deine Crew ist wieder öffentlich!"
    return False, "Es scheint als wärst du nicht in einer Crew."


command = Cmd(
    execute=execute,
    help_text=help_text,
    params_required=0,
    admin_required=False,
    voice_required=True,
    creator_only=True,
)
