from typing import Callable

from adam.commands.bash.bash_completer import BashCompleter
from adam.commands.command import Command
from adam.utils_k8s.app_clusters import AppClusters
from adam.utils_k8s.app_pods import AppPods
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.pod_exec_result import PodExecResult
from adam.repl_state import BashSession, ReplState, RequiredState
from adam.utils_k8s.statefulsets import StatefulSets
from build.lib.adam.utils_k8s.cassandra_nodes import CassandraNodes

class Bash(Command):
    COMMAND = 'bash'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Bash, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Bash.COMMAND

    def required(self):
        return [RequiredState.CLUSTER_OR_POD, RequiredState.APP_APP]

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0, args_to_check=2)
        if not self.validate_state(state):
            return state

        def _run(state_changed: bool, cli: Callable[[str], None]):
            if state.in_repl:
                if state_changed:
                    r = self.exec_with_dir(state, args)
                else:
                    r = self.exec_with_dir(s0, args)

                if not r:
                    state.exit_bash()

                    return 'inconsistent pwd'

                return r
            else:
                cli(' '.join(args))

                return state

        if state.device == ReplState.A:
            def cli(command: str):
                if state.app_pod:
                    AppPods.exec(state.app_pod, state.namespace, command, show_out=True)
                elif state.app_app:
                    AppClusters.exec(AppPods.pod_names(state.namespace, state.app_env, state.app_app), state.namespace, command, action='bash', show_out=True)

            return _run(s0.app_env != state.app_env or s0.app_app != state.app_app or s0.app_pod != state.app_pod, cli)

        def cli(command: str):
            if state.pod:
                CassandraNodes.exec(state.pod, state.namespace, command, show_out=True)
            elif state.sts:
                CassandraClusters.exec(state.sts, state.namespace, command, action='bash', show_out=True)

        return _run(s0.sts != state.sts or s0.pod != state.pod, cli)

    def exec_with_dir(self, state: ReplState, args: list[str]) -> list[PodExecResult]:
        session_just_created = False
        if not args:
            session_just_created = True
            session = BashSession(state.device)
            state.enter_bash(session)

        if state.bash_session:
            if args != ['pwd']:
                if args:
                    args.append('&&')
                args.extend(['pwd', '>', f'/tmp/.qing-{state.bash_session.session_id}'])

            if not session_just_created:
                if pwd := state.bash_session.pwd(state):
                    args = ['cd', pwd, '&&'] + args

        command = ' '.join(args)

        rs = []

        if state.device == ReplState.A:
            if state.app_pod:
                rs = [AppPods.exec(state.app_pod, state.namespace, command,
                                        show_out=not session_just_created, shell='bash')]
            elif state.app_app:
                rs = AppClusters.exec(AppPods.pod_names(state.namespace, state.app_env, state.app_app), state.namespace, command, action='bash',
                                            show_out=not session_just_created, shell='bash')
        else:
            if state.pod:
                rs = [CassandraNodes.exec(state.pod, state.namespace, command,
                                        show_out=not session_just_created, shell='bash')]
            elif state.sts:
                rs = CassandraClusters.exec(state.sts, state.namespace, command, action='bash',
                                            show_out=not session_just_created, shell='bash')

        return rs

    def completion(self, state: ReplState):
        if state.device == ReplState.A and state.app_app:
            return { Bash.COMMAND: BashCompleter(lambda: []) } | \
                   {f'@{p}': {Bash.COMMAND: BashCompleter(lambda: [])} for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}
        elif state.sts:
            return { Bash.COMMAND: BashCompleter(lambda: []) } | \
                   {f'@{p}': {Bash.COMMAND: BashCompleter(lambda: [])} for p in StatefulSets.pod_names(state.sts, state.namespace)}

        return {}

    def help(self, _: ReplState):
        return f'{Bash.COMMAND} [pod-name] [bash-commands] [&]\t run bash on the Cassandra nodes'