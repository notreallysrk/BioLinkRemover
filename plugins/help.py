"""Paginated, command-accurate Help Center for BioLinkRemover."""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatType, ButtonStyle

import config
from Client.helpers import is_user_admin
from Client.premium import premium_button, premium_emoji


# Keep this guide aligned with commands that are actually registered by the bot.
PAGES = [
    {
        "title": "Welcome to BioLinkRemover",
        "icon": "help",
        "intro": (
            "Your group's first line of defence against unwanted profile-bio links, "
            "suspicious websites and blacklisted words."
        ),
        "sections": [
            ("What the bot checks", "When a member sends a message, the bot checks their Telegram bio. Group admins and approved users are exempt."),
            ("What happens on a match", "The triggering message is deleted and the group’s configured action is applied: Ban, Mute or Kick."),
            ("Getting started", "Add the bot to your group, promote it to administrator and grant the permissions needed to delete messages and restrict or remove members."),
        ],
        "tip": "Use the buttons below to browse setup, protection and admin commands.",
    },
    {
        "title": "Quick Setup Guide",
        "icon": "source",
        "intro": "Set up protection in a few simple steps.",
        "sections": [
            ("01 · Add the bot", "Add BioLinkRemover to your group and promote it to administrator."),
            ("02 · Check permissions", "Enable Delete Messages, Ban Users and Invite Users as needed for your chosen moderation action."),
            ("03 · Choose a punishment", "Run /config and select Ban, Mute or Kick. You can also use /config ban, /config mute or /config kick."),
            ("04 · Protect new members", "Run /newuser to open the New User Protection panel. Enable it and choose how long new members should be limited to text-only messages."),
            ("05 · Trust selected members", "Use /approve for members who should be exempt from bio scanning."),
        ],
        "tip": "The bot must remain an administrator for moderation actions to work.",
    },
    {
        "title": "Approval & Whitelist",
        "icon": "admins",
        "intro": "Manage members who should be excluded from bio scanning. These commands are for group administrators.",
        "commands": [
            ("/approve", "Approve a member. Reply to their message, or provide a user ID or @username."),
            ("/unapprove", "Remove a member from the approved list. Uses the same target formats as /approve."),
            ("/approved", "Display the members currently approved in this group."),
            ("/unapproveall", "Clear the entire approved list for this group."),
        ],
        "examples": [
            "/approve @username",
            "/approve 123456789",
            "/unapprove @username",
        ],
        "tip": "Approved members are skipped by the bio scanner. Removing approval makes them eligible for scanning again.",
    },
    {
        "title": "Group Protection & Settings",
        "icon": "auth",
        "intro": "Control how the bot protects your group.",
        "commands": [
            ("/config", "Open the punishment selection panel and view the current mode."),
            ("/config ban", "Delete the violating message and ban the member."),
            ("/config mute", "Delete the violating message and restrict the member from chatting."),
            ("/config kick", "Delete the violating message and remove the member from the group."),
            ("/newuser", "Open the New User Protection panel to enable or disable temporary text-only restrictions and set their duration."),
        ],
        "tip": "Only group administrators can change these settings. The selected punishment is saved separately for each group.",
    },
    {
        "title": "Owner & Maintenance Commands",
        "icon": "owner",
        "intro": "These commands are available only to the configured owner and authorized sudo users, in private chat.",
        "commands": [
            ("/stats", "Show registered user and group totals."),
            ("/gcast <text>", "Send a text broadcast to all registered groups. You can also reply to a message with /gcast."),
            ("/ucast <text>", "Send a text broadcast to users who started the bot. You can also reply to a message with /ucast."),
            ("/update", "Check for available source updates and open the update workflow."),
            ("/updatehistory", "Show recent update and rollback history."),
        ],
        "tip": "Broadcasts and source updates are privileged operations. Double-check your message or update selection before proceeding.",
    },
    {
        "title": "Troubleshooting & FAQ",
        "icon": "help",
        "intro": "Quick checks for the most common setup problems.",
        "sections": [
            ("The bot does not delete messages", "Make sure it is an administrator and has Delete Messages permission."),
            ("Mute, kick or ban is not working", "Check that the bot has the relevant administrator permission and that its role is high enough to restrict or remove the target member."),
            ("A trusted member is still scanned", "Run /approved to verify the member is listed in this group. Approval is group-specific."),
            ("New User Protection is not applying", "Open /newuser and confirm the feature is enabled. Check that the bot can restrict members."),
            ("Where can I get more help?", "Use the Support button in the main menu, or contact your group owner/admin for permission and configuration issues."),
        ],
        "tip": "Telegram permissions and role hierarchy can prevent actions even when the bot command itself works.",
    },
]


def help_keyboard(page: int) -> InlineKeyboardMarkup:
    page = max(0, min(page, len(PAGES) - 1))
    navigation = []
    if page > 0:
        navigation.append(
            premium_button("Previous", "back", ButtonStyle.PRIMARY, callback_data=f"help_page:{page - 1}")
        )
    navigation.append(
        premium_button(f"{page + 1} / {len(PAGES)}", "queue", ButtonStyle.DANGER, callback_data="help_page:noop")
    )
    if page < len(PAGES) - 1:
        navigation.append(
            premium_button("Next", "skip", ButtonStyle.PRIMARY, callback_data=f"help_page:{page + 1}")
        )

    return InlineKeyboardMarkup([
        navigation,
        [premium_button("Main Menu", "home", ButtonStyle.SUCCESS, callback_data="start_pm")],
    ])


def render_help_page(page: int) -> str:
    data = PAGES[max(0, min(page, len(PAGES) - 1))]
    lines = [
        f"{premium_emoji('help', '📚')} <b>B I O L I N K R E M O V E R · HELP CENTER</b>",
        f"<i>{page + 1:02d} / {len(PAGES):02d}</i>",
        "",
        f"{premium_emoji(data['icon'], '🛡️')} <b>{data['title']}</b>",
        f"<i>{data['intro']}</i>",
        "",
    ]

    for heading, body in data.get("sections", []):
        lines.extend([f"<b>▸ {heading}</b>", body, ""])

    for command, description in data.get("commands", []):
        lines.extend([f"<code>{command}</code>", description, ""])

    if data.get("examples"):
        lines.append(f"{premium_emoji('source', '💡')} <b>Examples</b>")
        lines.extend(f"<code>{example}</code>" for example in data["examples"])
        lines.append("")

    lines.extend([
        "<blockquote>"
        f"{premium_emoji('source', '💡')} <b>TIP</b> · {data['tip']}"
        "</blockquote>",
        "<i>Choose Previous or Next to explore the guide.</i>",
    ])
    return "\n".join(lines)


async def show_help(client: Client, target, page: int):
    page = max(0, min(page, len(PAGES) - 1))
    text = render_help_page(page)
    keyboard = help_keyboard(page)
    if isinstance(target, CallbackQuery):
        await target.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await target.reply_text(text=text, reply_markup=keyboard)


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else 0
    is_owner = user_id == config.OWNER_ID or user_id in config.SUDO_USERS

    if message.chat.type == ChatType.PRIVATE:
        await show_help(client, message, 0)
        return

    if await is_user_admin(client, message.chat.id, user_id) or is_owner:
        await show_help(client, message, 0)
        return

    await message.reply_text(
        f"{premium_emoji('cancel', '❌')} <b>Access Denied</b>\n\n"
        "The group Help Center is available to administrators. Open the bot in private chat to view the general guide."
    )


@Client.on_callback_query(filters.regex(r"^help_page:(\d+|noop)$"))
async def help_page_callback(client: Client, callback_query: CallbackQuery):
    if callback_query.data.endswith(":noop"):
        await callback_query.answer(f"Help page {len(PAGES)} sections", show_alert=False)
        return
    page = int(callback_query.data.split(":", 1)[1])
    await callback_query.answer()
    await show_help(client, callback_query, page)


@Client.on_callback_query(filters.regex(r"^help_pm$"))
async def help_pm_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    await show_help(client, callback_query, 0)
