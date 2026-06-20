class EmailChannel:

    @staticmethod
    def send(
        *,
        to,
        subject,
        message,
        attachments=None,
    ):

        print("\n========== EMAIL ==========")
        print("TO:", to)
        print("SUBJECT:", subject)
        print("MESSAGE:")
        print(message)

        if attachments:
            print("ATTACHMENTS:")
            for attachment in attachments:
                print(" -", attachment)

        print("===========================\n")

        return True