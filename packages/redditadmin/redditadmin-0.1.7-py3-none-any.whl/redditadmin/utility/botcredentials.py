from abc import ABCMeta, abstractmethod


class BotCredentials(metaclass=ABCMeta):
    """
    Encapsulates the bot's credentials
    """

    @property
    @abstractmethod
    def password(self) -> str:
        """Retrieve the bot's Password"""
        ...

    @property
    @abstractmethod
    def client_secret(self) -> str:
        """Retrieve the bot's Client Secret"""
        ...

    @property
    @abstractmethod
    def client_id(self) -> str:
        """Retrieve the bot's Client ID"""
        ...

    @property
    @abstractmethod
    def user_agent(self) -> str:
        """Retrieve the bot's User Agent"""
        ...

    @property
    @abstractmethod
    def username(self) -> str:
        """Retrieve the bot's Username"""
        ...


class BotCredentialsImplementation(BotCredentials):

    def __init__(
            self,
            user_agent,
            client_id,
            client_secret,
            username,
            password
    ):
        self.__user_agent = user_agent
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__username = username
        self.__password = password

    @property
    def user_agent(self) -> str:
        return self.__user_agent

    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self):
        return self.__client_secret

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password


class InvalidBotCredentialsError(Exception):
    """
    Raised when provided bot credentials are invalid
    """

    def __init__(self, *args):
        super().__init__(self, args)
