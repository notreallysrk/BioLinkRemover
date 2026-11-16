
"""Premium category-based Help Center for BioLinkRemover."""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatType, ButtonStyle

import config
from Client.helpers import is_user_admin
from Client.premium import premium_button, premium_emoji


CATEGORIES = [
    {
        "id": "setup",
        "title": "Quick Setup",
        "icon": "add",
        "intro": "Get BioLinkRemover ready to protect your Telegram group.",
        "items": [
            ("1. Add the bot", "Add BioLinkRemover to your group and promote it to administrator."),
            ("2. Grant permissions", "Enable Delete Messages and the moderation permissions required for your selected action."),
            ("3. Configure protection", "Use /config to choose Ban, Mute or Kick."),
            ("4. Protect new members", "Use /newuser to configure temporary text-only restrictions."),
        ],
        "tip": "The bot must be an administrator. Its role must be high enough to moderate the target member.",
    },
    {
        "id": "approval",
        "title": "Approval & Whitelist",
        "icon": "admins",
        "intro": "Approved members are excluded from the bio scanner.",
        "commands": [
            ("/approve", "Approve a member. Reply to their message or provide a user ID / @username."),
            ("/unapprove", "Remove a member from the approved list. Supports reply, user ID or @username."),
            ("/approved", "Show the members approved in this group."),
            ("/unapproveall", "Clear the approved list for this group."),
        ],
        "examples": [
            "/approve @username",
            "/approve 123456789",
            "/unapprove @username",
        ],
        "tip": "Approval is group-specific. Use /approved to confirm the current list.",
    },
    {
        "id": "moderation",
        "title": "Moderation Settings",
        "icon": "auth",
        "intro": "Choose what happens when a member violates the bio protection rules.",
        "commands": [
            ("/config", "Open the punishment selection panel and view the current mode."),
            ("/config ban", "Delete the violating message and ban the member."),
            ("/config mute", "Delete the violating message and restrict the member from chatting."),
            ("/config kick", "Delete the violating message and remove the member from the group."),
        ],
        "tip": "Only group administrators can change the punishment mode. The setting is saved per group.",
    },
    {
        "id": "newmembers",
        "title": "New Member Protection",
        "icon": "blacklist",
        "intro": "Temporarily limit new members to text-only messages for a chosen duration.",
        "commands": [
            ("/newuser", "Open the New User Protection panel. Enable or disable protection and choose a restriction duration."),
        ],
        "items": [
            ("Status", "The panel shows whether protection is enabled and the current restriction duration."),
            ("Duration", "Choose a preset duration or enter a custom duration such as 90m, 18h or 2d."),
            ("Restore", "When protection is disabled, active restrictions are lifted by the feature."),
        ],
        "tip": "Only group administrators can manage this panel. The supported custom range is 30 minutes to 365 days.",
    },
    {
        "id": "admins",
        "title": "Admin Guide",
        "icon": "admins",
        "intro": "Group management commands are intended for administrators.",
        "items": [
            ("Who can use them?", "Group administrators can use /approve, /unapprove, /unapproveall, /approved, /config and /newuser."),
            ("Bot permissions", "Give the bot the permissions needed for deleting messages and applying the selected restriction."),
            ("Role hierarchy", "The bot cannot restrict or remove an administrator whose role is above the bot."),
        ],
        "tip": "Use the commands in the group where you want the settings to apply.",
    },
    {
        "id": "owner",
        "title": "Owner Commands",
        "icon": "owner",
        "intro": "These commands are restricted to the configured owner and authorized sudo users in private chat.",
        "commands": [
            ("/update", "Check for available source updates and open the update workflow."),
            ("/updatehistory", "Show recent update and rollback history."),
            ("/selfpromo", "Show automatic self-promotion status."),
            ("/selfpromo on", "Enable automatic promotion every 24 hours."),
            ("/selfpromo off", "Disable automatic promotion."),
            ("/selfpromo run", "Run a self-promotion broadcast immediately."),
        ],
        "tip": "Owner commands do not respond to unauthorized users.",
    },
    {
        "id": "broadcast",
        "title": "Broadcast Tools",
        "icon": "updates",
        "intro": "Send announcements from the bot's private chat. Owner / sudo access is required.",
        "commands": [
            ("/gcast <text>", "Broadcast text to all registered groups. You can also reply to a message with /gcast."),
            ("/ucast <text>", "Broadcast text to users who have started the bot. You can also reply to a message with /ucast."),
        ],
        "examples": [
            "/gcast Hello everyone!",
            "/ucast A new update is available.",
        ],
        "tip": "Check the content carefully before sending a broadcast.",
    },
    {
        "id": "stats",
        "title": "Statistics",
        "icon": "stats",
        "intro": "View basic usage information for the bot.",
        "commands": [
            ("/stats", "Show the total number of registered users and groups. Owner / sudo only, in private chat."),
        ],
        "tip": "Users and groups are registered when they start or interact with the bot as handled by the project.",
    },
    {
        "id": "faq",
        "title": "Help & Troubleshooting",
        "icon": "help",
        "intro": "Quick solutions for common setup and moderation issues.",
        "items": [
            ("Messages are not deleted", "Confirm the bot is an administrator with Delete Messages permission."),
            ("Mute / kick / ban fails", "Check the relevant admin permission and make sure the bot's role is high enough."),
            ("A trusted user is scanned", "Run /approved in that group and confirm the member is listed."),
            ("New User Protection is inactive", "Run /newuser and verify that protection is enabled."),
            ("Still need help?", "Contact your group owner/admin or use the Support button in the bot's main menu."),
        ],
        "tip": "Telegram permissions and role hierarchy can prevent an action even when the command is correct.",
    },
]


def home_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        premium_button("Quick Setup", "add", ButtonStyle.PRIMARY, callback_data="help_cat:setup"),
        premium_button("Approval", "admins", ButtonStyle.PRIMARY, callback_data="help_cat:approval"),
        premium_button("Settings", "auth", ButtonStyle.PRIMARY, callback_data="help_cat:moderation"),
        premium_button("New Members", "blacklist", ButtonStyle.PRIMARY, callback_data="help_cat:newmembers"),
        premium_button("Admins", "admins", ButtonStyle.PRIMARY, callback_data="help_cat:admins"),
        premium_button("Owner", "owner", ButtonStyle.PRIMARY, callback_data="help_cat:owner"),
        premium_button("Broadcast", "updates", ButtonStyle.PRIMARY, callback_data="help_cat:broadcast"),
        premium_button("Statistics", "stats", ButtonStyle.PRIMARY, callback_data="help_cat:stats"),
        premium_button("FAQ", "help", ButtonStyle.PRIMARY, callback_data="help_cat:faq"),
    ]

    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    rows.append([
        premium_button(
            "Main Menu",
            "home",
            ButtonStyle.SUCCESS,
            callback_data="start_pm",
        )
    ])

    return InlineKeyboardMarkup(rows)


def category_keyboard(index: int) -> InlineKeyboardMarkup:
    previous = (index - 1) % len(CATEGORIES)
    following = (index + 1) % len(CATEGORIES)

    return InlineKeyboardMarkup([
        [
            premium_button(
                "⬅️ Prev",
                "back",
                ButtonStyle.PRIMARY,
                callback_data=f"help_cat:{CATEGORIES[previous]['id']}",
            ),
            premium_button(
                "🏠 Main Menu",
                "home",
                ButtonStyle.SUCCESS,
                callback_data="help_home",
            ),
            premium_button(
                "Next ➡️",
                "skip",
                ButtonStyle.PRIMARY,
                callback_data=f"help_cat:{CATEGORIES[following]['id']}",
            ),
        ]
    ])


def render_home() -> str:
    return (
        f"{premium_emoji('help', '📚')} "
        "<b>B I O L I N K R E M O V E R</b>\n"
        "<b>HELP CENTER & MANUAL</b>\n\n"
        "Explore commands, group protection and bot settings "
        "using the category buttons below.\n\n"
        f"{premium_emoji('auth', '🛡️')} <b>Group Protection</b>\n"
        "Scan member bios and take action on unwanted links "
        "or blacklisted content.\n\n"
        f"{premium_emoji('source', '💡')} "
        "<i>Select a section to view its guide and commands.</i>"
    )


def render_category(index: int) -> str:
    data = CATEGORIES[index]

    lines = [
        f"{premium_emoji(data['icon'], '📘')} <b>{data['title']}</b>",
        f"<i>{data['intro']}</i>",
        f"<i>SECTION {index + 1:02d} / {len(CATEGORIES):02d}</i>",
        "",
    ]

    for heading, body in data.get("items", []):
        lines.extend([
            f"<b>▸ {heading}</b>",
            body,
            "",
        ])

    for command, description in data.get("commands", []):
        lines.extend([
            f"<code>{command}</code>",
            description,
            "",
        ])

    if data.get("examples"):
        lines.append(
            f"{premium_emoji('source', '💡')} <b>Examples</b>"
        )
        lines.extend(
            f"<code>{example}</code>"
            for example in data["examples"]
        )
        lines.append("")

    lines.extend([
        "<blockquote>"
        f"{premium_emoji('source', '💡')} "
        f"<b>TIP</b> · {data['tip']}"
        "</blockquote>",
        "<i>Use the navigation buttons to browse other sections.</i>",
    ])

    return "\n".join(lines)


async def show_home(target):
    if isinstance(target, CallbackQuery):
        await target.edit_message_text(
            text=render_home(),
            reply_markup=home_keyboard(),
        )
    else:
        await target.reply_text(
            text=render_home(),
            reply_markup=home_keyboard(),
        )


async def show_category(target, category_id: str):
    index = next(
        (
            i for i, item in enumerate(CATEGORIES)
            if item["id"] == category_id
        ),
        0,
    )

    if isinstance(target, CallbackQuery):
        await target.edit_message_text(
            text=render_category(index),
            reply_markup=category_keyboard(index),
        )
    else:
        await target.reply_text(
            text=render_category(index),
            reply_markup=category_keyboard(index),
        )


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else 0
    is_owner = (
        user_id == config.OWNER_ID
        or user_id in config.SUDO_USERS
    )

    if message.chat.type == ChatType.PRIVATE:
        await show_home(message)
        return

    if await is_user_admin(
        client,
        message.chat.id,
        user_id,
    ) or is_owner:
        await show_home(message)
        return

    await message.reply_text(
        f"{premium_emoji('cancel', '❌')} <b>Access Denied</b>\n\n"
        "The group Help Center is available to administrators. "
        "Open the bot in private chat to view the general guide."
    )


@Client.on_callback_query(filters.regex(r"^help_home$"))
async def help_home_callback(
    client: Client,
    callback_query: CallbackQuery,
):
    await callback_query.answer()
    await show_home(callback_query)


@Client.on_callback_query(
    filters.regex(r"^help_cat:([a-z_]+)$")
)
async def help_category_callback(
    client: Client,
    callback_query: CallbackQuery,
):
    category_id = callback_query.data.split(":", 1)[1]

    if category_id not in {
        item["id"] for item in CATEGORIES
    }:
        await callback_query.answer(
            "Section not found.",
            show_alert=True,
        )
        return

    await callback_query.answer()
    await show_category(callback_query, category_id)


@Client.on_callback_query(filters.regex(r"^help_pm$"))
async def help_pm_callback(
    client: Client,
    callback_query: CallbackQuery,
):
    await callback_query.answer()
    await show_home(callback_query)
