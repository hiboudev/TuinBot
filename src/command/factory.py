from command.commands import Command, Commands


class CommandFactory:

    @staticmethod
    def get_command(name: str) -> [Command, None]:
        for command_class in Commands.LIST:
            if command_class.name() == name:
                return command_class

        return None
