import argparse
import os
from pathlib import Path

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_str2yaml import arg_str2yaml
from ul_py_tool.utils.aseembly import AssemblyFile, AssemblyTarget
from ul_py_tool.utils.colors import FG_GREEN, FG_YELLOW, NC
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper


class CmdCloneComponents(Cmd):
    """Клонирует все компоненты из assembly.yaml для заданного target"""

    release_target: str
    assembly_file: AssemblyFile
    assembly_target: AssemblyTarget | None = None
    force: bool = False

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--release-target', dest='release_target', type=str, required=True)
        parser.add_argument('--assembly-file', dest='assembly_file', type=arg_str2yaml, required=True, default='assembly.yaml')
        parser.add_argument('--force', dest='force', action='store_true',
                            help='Force re-clone even if directories exist')

    def run(self) -> None:
        stepper = Stepper()
        cwd = Path.cwd()

        with stepper.step(f'{FG_GREEN}check target exists{NC}'):
            if self.release_target not in self.assembly_file.targets:
                raise argparse.ArgumentTypeError(f'Target {self.release_target} not found in assembly file')
            self.assembly_target = self.assembly_file.targets[self.release_target]

        with stepper.step(f'{FG_GREEN}clone required repositories{NC}') as stp:
            cloned_count = 0
            skipped_count = 0

            for component_name, component in self.assembly_file.components.items():
                component_dir = cwd / component.directory

                # Пропускаем уже клонированные (если не --force)
                if component_dir.exists() and not self.force:
                    print(f'{FG_YELLOW}⊙ {component_name}: already exists, skipping (use --force to re-clone){NC}')
                    skipped_count += 1
                    continue

                if component_dir.exists() and self.force:
                    import shutil
                    shutil.rmtree(component_dir)

                os.makedirs(component_dir, exist_ok=False)

                run_command(
                    [f'git clone --depth 1 --branch {component.tag} {component.repository} .'],
                    cwd=str(component_dir)
                )

                run_command(
                    ['git submodule sync --recursive && git submodule update --init --recursive'],
                    cwd=str(component_dir)
                )

                print(f'{FG_GREEN}✓ {component_name}: cloned {component.tag}{NC}')
                cloned_count += 1

            print(f'\n{FG_GREEN}Summary:{NC}')
            print(f'  Cloned: {cloned_count}')
            print(f'  Skipped: {skipped_count}')
            print(f'  Total: {len(self.assembly_file.components)}')

