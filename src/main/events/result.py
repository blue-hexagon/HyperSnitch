class EventResult:
    def __init__(self):
        """
        Initializes the match event result.
        Initially, no match has been found, and no notification has been sent.
        """
        self._match_found = False
        self._notification_sent = False

    def reset(self) -> None:
        """
        Resets the match state and notification status.
        """
        self._match_found = False
        self._notification_sent = False

    def set_match(self) -> None:
        """
        Sets the state to indicate a match has been found.
        """
        self._match_found = True

    @property
    def match_found(self) -> bool:
        """
        Returns whether a match has been found.
        """
        return self._match_found

    @property
    def notification_sent(self) -> bool:
        """
        Returns whether an email notification has been sent.
        """
        return self._notification_sent

    def send_notification(self) -> bool:
        """
        Simulates sending a notification (e.g., an email).
        Sets the state to indicate a notification has been sent.
        """
        if self._match_found and not self._notification_sent:
            self._notification_sent = True
            return True
        else:
            return False
