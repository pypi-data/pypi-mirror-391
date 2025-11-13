import subprocess

from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState

class Kubectl(Command):
    COMMAND = 'k'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Kubectl, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Kubectl.COMMAND

    def required(self):
        return RequiredState.NAMESPACE

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        subprocess.run(["kubectl"] + args)

        return state

    def completion(self, state: ReplState):
        return super().completion(state)


    def help(self, _: ReplState):
        return f'{Kubectl.COMMAND} \t run a kubectl command'