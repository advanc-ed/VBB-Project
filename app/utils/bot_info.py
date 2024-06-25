import logging


def bot_info(bot_information):
    """This information comes on bot startup"""
    logging.info(f"Name - {bot_information.full_name}")
    logging.info(f"Username - @{bot_information.username}")
    logging.info(f"ID - {bot_information.id}")

    states = {
        True: "Enabled",
        False: "Disabled",
    }

    logging.debug(f"Groups Mode - {states[bot_information.can_join_groups]}")
    logging.debug(
        f"Privacy Mode - {states[not bot_information.can_read_all_group_messages]}")
    logging.debug(f"Inline Mode - {states[bot_information.supports_inline_queries]}")
