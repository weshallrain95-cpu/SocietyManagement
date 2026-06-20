class WhatsAppChannel:

    @staticmethod
    def send(
        *,
        to,
        message,
        attachment=None,
    ):

        print("\n======= WHATSAPP =======")
        print("TO:", to)
        print("MESSAGE:")
        print(message)

        if attachment:
            print("ATTACHMENT:")
            print(attachment)

        print("========================\n")

        return True