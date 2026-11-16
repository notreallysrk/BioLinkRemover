"""Small in-process caches shared by plugin handlers."""
USER_IDS_CACHE: set[int] = set()
GROUP_IDS_CACHE: set[int] = set()
GROUP_CONFIG_CACHE: dict[int, str] = {}
APPROVED_USERS_CACHE: dict[int, set[int]] = {}
GROUP_ADMINS_CACHE: dict[int, tuple[set[int], float]] = {}
NEWUSER_CONFIG_CACHE: dict[int, dict] = {}
