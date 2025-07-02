from enum import IntEnum

import disnake


class Color(IntEnum):
    GRAY = 0x2F3136
    GREEN = 0x00FF00
    RED = 0xFF0000
    BLUE = 0x0000FF


class ClientInfo(IntEnum):
    ZONYX = .
    BOT_GUILD_ID = .  # Development


class ChannelsInfo(IntEnum):
    VERIFY_LOGS_CHANNEL = .
    FEEDBACK_CHANNEL = .
    VERIFY_CATEGORY_ID = .
    WARNS_LOG_CHANNEL = .


class RolesInfo(IntEnum):
    NEW_ROLE = .
    DENY_VERIFY_ROLE = .

    SUPPORT_ROLE = .


class ChiefRoles(IntEnum):
    MARMOK = .
    ADMIN = .
    SQUAD = .
    ADMINISTRATOR = .
    DEVELOPER = .
    SECURITY = .


default_error = (disnake.Forbidden, disnake.HTTPException)

full_errors = (disnake.Forbidden, disnake.HTTPException, disnake.NotFound, disnake.InvalidData, TypeError, ValueError)
