# SQL Generate Table TK
# Imports from other dependencies.  # NOQA
# from sqlalchemy import (
#     Date,
#     DateTime,
#     Float,
#     Integer,
#     Text,
#     Time,
#     Unicode,
# )
#
#
# def get_db_type_from_text(typeString):
#     if typeString == 'INTEGER':
#         return Integer
#     elif typeString == 'FLOAT':
#         return Float
#     elif typeString == 'TEXT':
#         return Unicode(255)
#     elif typeString == 'LONGTEXT':
#         return Text
#     elif typeString == 'DATE':
#         return Date
#     elif typeString == 'TIME':
#         return Time
#     elif typeString == 'DATETIME':
#         return DateTime
#     # I guess Text will do as a default but hopefully this ELSE clause is never
#     # triggered.
#     else:
#         return Text
#
#
# def get_connection_string(dialect):
#     if dialect == 'postgresql':
#         return 'postgres://'
#     elif dialect == 'sqlite':
#         return 'sqlite://'
#     elif dialect == 'mysql':
#         return 'mysql://'
#     else:
#         raise ValueError(
#             '%s is not a dialect of SQL accepted by this app.' % (
#                 dialect
#             )
#         )
pass
