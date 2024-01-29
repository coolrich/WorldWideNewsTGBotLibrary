import logging
from enum import Enum
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn

logger = logging.getLogger(__name__)


class CountryCodes(Enum):
    UA = [kbn.UA.value, "Новини України"]
    WORLD = [kbn.WORLD.value, "Новини Світу"]

    @staticmethod
    def get_member_by_value(item):
        """
        Get the member of `CountryCodes` enum that corresponds to the given value.

        Args:
            item (str): The value to search for in the `CountryCodes` enum.

        Returns:
            CountryCodes: The member of `CountryCodes` enum that corresponds to the given value.

        Raises:
            KeyError: If the value is not found in the `CountryCodes` enum.
        """

        logger.debug("In CountryCodes in method get_member_by_value")
        if isinstance(item, str):
            logger.debug("In CountryCodes in method get_member_by_value: " + str(item))
            for country_code in CountryCodes:
                if str(item) in country_code.value:
                    logger.debug("In CountryCodes return value: " + str(country_code))
                    return country_code
        raise KeyError
