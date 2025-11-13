###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

# Activate this setting to log all SQL queries
POSTGRESQL_LOG_QUERIES: bool = False

# Connection settings
POSTGRESQL_CONNECTION_DATABASE: str = None
POSTGRESQL_CONNECTION_PASSWORD: str = None
POSTGRESQL_CONNECTION_PORT: int = 5432
POSTGRESQL_CONNECTION_HOST: str = None
POSTGRESQL_CONNECTION_USER: str = None
POSTGRESQL_POOL_MAX_SIZE: int = 10
