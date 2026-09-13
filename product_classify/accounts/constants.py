from enum import IntEnum, StrEnum


class RoleCodes(StrEnum):
    HANDBOOK_EXECUTIVE =              "handbook-executive"
    HANDBOOK_USER =                   "handbook-user"
    BUILDER =                         "builder"
    TECHNOLOGIST =                    "technologist"
    CHIEF_MECHANIC_DEPT_EMPLOYEE =    "chief-mechanic-dept-employee"
    SALES_DEPT_EMPLOYEE =             "sales-dept-employee"
    PRODUCTION_DEPT_EMPLOYEE =        "production-dept-employee"
    CLIENT =                          "client"
    ECONOMIC_PLANNING_DEPT_EMPLOYEE = "economic-planning-dept-employee"


class RoleConsts(IntEnum):
    NAME_MAX_LENGTH =               100


class UserConsts(IntEnum):
    FIRST_NAME_MAX_LENGTH =         100
    MIDDLE_NAME_MAX_LENGTH =        100
    LAST_NAME_MAX_LENGTH =          100
    EMAIL_MAX_LENGTH =              100
    PHONE_NUMBER_MAX_LENGTH =       18
    PASSWORD_MAX_LENGTH =           128
