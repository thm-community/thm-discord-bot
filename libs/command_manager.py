"""Command Manager module to handle permissions checking and other utilities.

This module manages the permissions checking system in a standardized and consistent method.
Main usage is a decorator method that is called after the bot listener's method, but before the
command itself to properly perform permission checks prior to command execution.
Module also includes a bot error message method and input sanitation check.
i.e.

Typical usage example:
    import libs.command_manager as command_manager
    from discord.ext import commands

    @commands.command(...)        # Required bot listener method
    @command_manager.check(roles=["admin",
                                  "mod",  ],
                           channels=["staff_channel",],)
    async fun_command(self, ctx, user_input=""): # Your command to be executed after the check
        if command_manager.is_sanitized(user_input):
            do_thing()
        else:
            command_manager.error_response(ctx, "not_sanitized")
        ...
"""
import libs.config as config
from discord.channel import DMChannel
from discord.ext import commands
import functools
import asyncio


# GLOBAL VARIABLES
ERROR_STRING = config.get_string("commands")
ROLE_IDS = config.get_config("roles")
CHANNEL_IDS = config.get_config("channels")
DEFAULT_BANNED = ["/", ";", "-", ">", "<", ":", "`", "\"", "|"]


def check(roles="",
          channels="",
          dm_flag=None):
    """Decorator to check role permissions and context for the user invoking a bot command.

    Wrap around a bot command to check appropriate permission and channel context of the executed command from
    the Context object provided by the bot's event listener method, and errors out if checks do not pass.
    String names of roles and channels are derived from config/config.json keys.
    All exceptions raised are inherited from Discord.ext.commands

    Args:
        roles: String array of whitelisted roles from config.json that the user must have .
        channels: String array of whitelisted channels from config.json that the command can be executed in.
        dm_flag: Boolean flag to set a DM-Only command if True, or public channels only command if False.

    Returns:
        Original method call that the method wraps around, and continues executing the command/method.
        If any checks fail, then will stop execution of the method and returns False after raising an exception.

    Raises:
        PrivateMessageOnly: Command is invoked in a public channel while arg dm_flag is True.
        NoPrivateMessage: Command is invoked in a DM while arg dm_flag is False.
        CommandInvokeError: Command is not invoked in the whitelist of arg channels.
        MissingAnyRole: Context.author does not have a role in the whitelist of arg roles.
    """
    
    def perm_check(cmd):
        """Wrapper method to allow our own method to be executed before the original method"""
        @functools.wraps(cmd)
        async def wrapper(*args, **kwargs):
            """Checks permissions of the message before executing command"""
            # wrapper() args is the original args passed to the command being checked
            # Second element of args will always be the discord message (Context object)
            ctx = args[1]
            if type(ctx) is not commands.Context:
                print("ERROR: Missing ctx variable in @check() call in", cmd.__name__, " command!")
                raise commands.MissingRequiredArgument(ctx)

            # 1. Checking if dm_flag is set and if message is in DMs
            if dm_flag is not None:
                try:
                    check_context(ctx, dm_flag)
                # Errors out if the message is not in the appropriate context
                # TODO: log exceptions to debug
                except commands.PrivateMessageOnly as e:
                    await error_response(ctx, "context_dm_only",
                                         delete_ctx=True)
                    return False
                except commands.NoPrivateMessage as e:
                    await error_response(ctx, "context_public_only",
                                         delete_msg=False)
                    return False

            # 2. Checking for if the message is in the list of channels provided. dm_flag = False for no DM
            if channels:
                dm_allowed = dm_flag is not False
                try:
                    check_channel(ctx, channels, dm_allowed)
                # Errors out if channel is not in the channels whitelist
                except commands.CommandInvokeError as e:
                    # TODO: log exception to debug
                    await error_response(ctx, "channel_not_allowed",
                                         delete_ctx=True)
                    return False

            # 3. Checking if the message author has a role in the list of whitelisted roles.
            if roles:
                try:
                    check_roles(ctx, roles)
                # Error out if the user does not have any role in the whitelisted roles.
                except commands.MissingAnyRole as e:
                    # TODO: log exception to debug
                    await error_response(ctx, "no_perm",
                                         delete_ctx=True)
                    return False

            # 4. If all checks succeeded, then executes the original command.
            return await cmd(*args, **kwargs)

        return wrapper

    return perm_check


async def is_sanitized(msg,
                       ctx=None,
                       err_msg="not_sanitized",
                       banned_chars=None):
    """Recursively checks user input for any forbidden characters.

    Checks if any character from a list of banned chars (None for default list) is present
    in any of string text in arg msg.
    Default banned characters are "/", ";", "-", ">", "<", ":", "`", "\"", "|"

    Args:
        msg: String or list of strings to be checked for sanitation.
        ctx: Original Discord Context object to allow response from the bot for error messages.
        err_msg: String of the key name in config.json["commands"], or error message string for bot to echo.
        banned_chars: List of chars that the msg will be checked against.

    Returns:
        Returns True if all text does not contain any banned chars, otherwise will throw an exception.

    Raises:
        BadArgument: Text contains a forbidden character.
    """
    if banned_chars:
        banned = banned_chars
    else:
        banned = DEFAULT_BANNED

    for text in msg:
        # Check to see if arg is a list to also recursively sanitize anything in it
        if type(text) is tuple or \
           type(text) is list:
            await is_sanitized(ctx, text)
        else:
            # Otherwise, check text for sanitation.
            has_banned_chars = [char for char in text if char in banned]

            if has_banned_chars:
                if ctx and err_msg:
                    await error_response(ctx, err_msg)
                # TODO: log exception to debug/tracking channel
                raise commands.BadArgument(message=msg)
    # If all text is sanitary, then return bool True
    return True


async def error_response(ctx, err_msg,
                         delete_msg=True,
                         delete_ctx=False):
    """Makes the bot send a response back to the ctx.channel as err_msg, and deletes the message automatically

    Args:
        ctx: Original Discord Context object to allow response from the bot for error messages.
        err_msg:
            Desired response message from the box, is derived from config.json["commands"], otherwise will
            use the err_msg string itself as the bot's error message.
        delete_msg: Deletes the bot's error message after 5 seconds if True
        delete_ctx: Deletes the ctx message (user's message) after 5 seconds if True
    """
    # Tries to retrieve ERROR_STRING[err_msg], but if not found, then defaults to err_msg
    error_output = ERROR_STRING.get(err_msg, err_msg)

    bot_message = await ctx.send(error_output)

    if delete_msg or delete_ctx:
        await asyncio.sleep(5)
        if delete_msg:
            await bot_message.delete()
        if delete_ctx and type(ctx.channel) is not DMChannel:
            await ctx.message.delete()


def check_context(ctx, dm_flag):
    """Checks if the context is correct (DMs or public channel)"""
    dm_message = type(ctx.channel) is DMChannel

    # If message is not a DM and the command is DM only (dm_flag True)
    if not dm_message and dm_flag:
        raise commands.PrivateMessageOnly
    # If message is a DM but the command is not allowed in DMs (dm_flag False)
    elif dm_message and not dm_flag:
        raise commands.NoPrivateMessage

    return dm_message


def check_channel(ctx, channels, dm_allowed):
    """Checks the current channel is valid for the command with arg channels"""
    if type(channels) is str:
        channels = [channels]
    # Converts arg channels into corresponding channel IDs, and check if DM is ok
    valid_channels = [CHANNEL_IDS[channel] for channel in channels]
    dm_appropriate = type(ctx.channel) is DMChannel and dm_allowed

    # Check if channel is in the list of channels and/or if DM is ok
    if ctx.channel.id not in valid_channels and not dm_appropriate:
        raise commands.CommandInvokeError(ctx)

    return True


def check_roles(ctx, roles):
    """Checks that the user has all the required roles."""
    if type(roles) is str:
        roles = [roles]
    user = ctx.author
    # Get the list of IDs from user.roles, and list of IDs from arg roles
    user_roles = [role.id for role in user.roles]
    req_roles = [ROLE_IDS[req_role] for req_role in roles]

    # Check intersection of roles in user_roles and req_roles.
    if not [role for role in user_roles if role in req_roles]:
        raise commands.MissingAnyRole(roles)

    return True
