import argparse
import os
import subprocess
import shutil
from pathlib import Path

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_str2yaml import arg_str2yaml
from ul_py_tool.utils.aseembly import AssemblyFile, AssemblyTarget
from ul_py_tool.utils.colors import FG_GREEN, FG_RED, NC
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper


class CmdRenderValues(Cmd):
    release_target: str | None = None
    assembly_file: AssemblyFile | None = None
    assembly_target: AssemblyTarget | None = None
    output_dir: str
    single_service: str | None = None
    vault_config_template: str
    skip_clone: bool = False
    debug: bool = False

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--release-target', dest='release_target', type=str, required=False, default=None)
        parser.add_argument('--assembly-file', dest='assembly_file', type=arg_str2yaml, required=False, default=None)
        parser.add_argument('--output-dir', dest='output_dir', type=str, required=False, default='secrets')
        parser.add_argument('--single-service', dest='single_service', type=str, default=None,
                            help='Service name for single service deployment (without assembly). If not set, uses assembly mode.')
        parser.add_argument('--vault-config-template', dest='vault_config_template', type=str,
                            required=False, default='vault-agent.hcl.tpl')
        parser.add_argument('--skip-clone', dest='skip_clone', action='store_true',
                            help='Skip cloning repositories (assumes they are already present)')
        parser.add_argument('--debug', dest='debug', action='store_true',
                            help='Debug log level')


    def run(self) -> None:
        stepper = Stepper()
        cwd = Path.cwd()

        with stepper.step(f'{FG_GREEN}check vault config template{NC}'):
            vault_config_tpl_path = cwd / self.vault_config_template
            if not vault_config_tpl_path.exists():
                raise FileNotFoundError(
                    f'{FG_RED}Vault Agent config template not found: {vault_config_tpl_path}\n'
                    f'Create vault-agent.hcl.tpl in project root.{NC}'
                )
            vault_config_template = vault_config_tpl_path.read_text()

        if self.single_service:
            self._render_single_service(cwd, vault_config_template, stepper)
        else:
            self._render_assembly(cwd, vault_config_template, stepper)

    def _render_single_service(self, cwd: Path, vault_config_template: str, stepper: Stepper) -> None:
        """Рендерит values.yaml для одного сервиса в .helm/values.yaml (для werf converge)"""
        with stepper.step(f'{FG_GREEN}render single service values{NC}'):
            tpl_path = cwd / '.helm' / 'values.tpl'
            dest_path = cwd / '.helm' / 'values.yaml'

            if not tpl_path.exists():
                raise FileNotFoundError(f'{FG_RED}Template not found: {tpl_path}{NC}')

            self._run_vault_agent(
                component_name=self.single_service,
                tpl_path=tpl_path,
                dest_path=dest_path,
                vault_config_template=vault_config_template,
                cwd=cwd,
            )

            print(f'{FG_GREEN}✓ {self.single_service}: {dest_path.relative_to(cwd)}{NC}')

    def _render_assembly(self, cwd: Path, vault_config_template: str, stepper: Stepper) -> None:
        """Рендерит values.yaml для множества компонентов из assembly.yaml"""
        with stepper.step(f'{FG_GREEN}check target exists{NC}'):
            if not self.release_target or not self.assembly_file:
                raise argparse.ArgumentTypeError(
                    f'{FG_RED}--release-target and --assembly-file required for assembly mode{NC}'
                )
            if self.release_target not in self.assembly_file.targets:
                raise argparse.ArgumentTypeError(
                    f'{FG_RED}Target {self.release_target} not found in assembly file{NC}'
                )
            self.assembly_target = self.assembly_file.targets[self.release_target]

        if not self.skip_clone:
            with stepper.step(f'{FG_GREEN}init required repositories{NC}'):
                for component in self.assembly_file.components.values():
                    component_dir = cwd / component.directory
                    os.makedirs(component_dir, exist_ok=False)
                    run_command(
                        [f'git clone --depth 1 --branch {component.tag} {component.repository} .'],
                        cwd=str(component_dir)
                    )
                    run_command(
                        ['git submodule sync --recursive && git submodule update --init --recursive'],
                        cwd=str(component_dir)
                    )

        with stepper.step(f'{FG_GREEN}render values for components{NC}') as stp:
            for component_name, component_config in self.assembly_file.components.items():
                values_dir = cwd / self.output_dir / component_name / \
                            f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}'
                values_dir.mkdir(parents=True, exist_ok=True)

                tpl_path = cwd / component_config.directory / '.helm' / 'values.tpl'
                dest_path = values_dir / 'values.yaml'

                if not tpl_path.exists():
                    stp.add_error(f'{FG_RED}Template not found for {component_name}: {tpl_path}{NC}')
                    continue

                try:
                    self._run_vault_agent(
                        component_name=component_name,
                        tpl_path=tpl_path,
                        dest_path=dest_path,
                        vault_config_template=vault_config_template,
                        cwd=cwd,
                    )
                    print(f'{FG_GREEN}✓ {component_name}: {dest_path.relative_to(cwd)}{NC}')
                except Exception as e:
                    stp.add_error(f'{FG_RED}Failed to render {component_name}: {e}{NC}')

    def _run_vault_agent(
        self,
        component_name: str,
        tpl_path: Path,
        dest_path: Path,
        vault_config_template: str,
        cwd: Path,
    ) -> None:
        """Генерирует временный конфиг и запускает Vault Agent"""
        vault_addr = os.getenv('VAULT_ADDR', 'http://192.168.10.96:8200')
        vault_role_id_file = os.getenv('VAULT_ROLE_ID_FILE', '/tmp/VAULT_ROLE_ID')
        vault_secret_id_file_original = os.getenv('VAULT_SECRET_ID_FILE', '/tmp/VAULT_SECRET_ID')

        # Создаём временную копию secret_id для этого компонента
        # (Vault Agent удаляет файл после использования)
        vault_secret_id_file_temp = f'/tmp/VAULT_SECRET_ID_{component_name}'
        shutil.copy(vault_secret_id_file_original, vault_secret_id_file_temp)

        # Генерируем временный конфиг из шаблона
        vault_config_content = vault_config_template.format(
            pid_file=f'/tmp/vault-agent-{component_name}.pid',
            vault_addr=vault_addr,
            role_id_file=vault_role_id_file,
            secret_id_file=vault_secret_id_file_temp,
            token_file=f'/tmp/vault-token-{component_name}',
            tpl_path=str(tpl_path.absolute()),
            dest_path=str(dest_path.absolute()),
        )

        temp_config_path = cwd / f'.vault-agent-{component_name}.hcl'
        temp_config_path.write_text(vault_config_content)

        try:
            log_level = 'debug' if self.debug else 'info'
            result = run_command(
                [f'vault agent -config={temp_config_path} -exit-after-auth -log-level={log_level}'],
                cwd=str(cwd),
                ignore_errors=True
            )

            if result.code != 0:
                raise RuntimeError(f'Vault agent failed:\n{result.stdout}')

            if not dest_path.exists():
                raise RuntimeError(f'Vault agent did not render: {dest_path}')

        finally:
            if temp_config_path.exists():
                temp_config_path.unlink()
            if os.path.exists(vault_secret_id_file_temp):
                os.remove(vault_secret_id_file_temp)
