class SMSChannel:

    @staticmethod
    def send(
        *,
        to,
        message,
    ):

        print("\n========== SMS ==========")
        print("TO:", to)
        print("MESSAGE:")
        print(message)
        print("=========================\n")

        return True