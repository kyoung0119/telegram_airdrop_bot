from pytz import timezone


class Config:
    API_ID = 0
    API_HASH = ""
    TOKEN = ""
    ADMINS = []
    DB_URI = ""
    DB_NAME = ""
    TIMEZONE = timezone("Asia/Jerusalem")
    LOG_CHANNEL = -0
    UPDATES_CHANNEL = -0
    UPDATES_GROUP = -0
    TEAM_GROUP = -0
    BOT_USERNAME = ""
    ELEMENTS_PER_PAGE = 10
    TOKENS_PER_INVITE = 1000
    TOKENS_FOR_TASK = 25000
    MAX_VERIFICATION_RETRIES = 3

    QUESTS_SITE = ""

    AIRDROP_WALLET = ""
    TOKEN_MINT = ""
    RPC_URL = ""
