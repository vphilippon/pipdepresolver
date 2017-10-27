import subprocess
import re

import click


CHECK_RE = r'^.* has requirement (?P<req>.+), but you have .*$'


@click.group()
def cli():
    pass


@cli.command('install')
@click.argument('src_file', type=click.Path(exists=True))
@click.pass_context
def install(ctx, src_file):
    """
    Resolve and install a set of requirements.
    """
    previous_freeze = []

    # Get in a cycle of `pip install -r src_file` & `pip check` & `pip install <reqs_to_fix>`.
    for round_nb in range(10):  # Max 10 rounds.
        click.echo('ROUND {}'.format(round_nb))

        # 1. Run a first `pip install -r src_file`.
        try:
            output = subprocess.check_output(['pip', 'install', '-r', src_file])
            click.echo(output)
        except subprocess.CalledProcessError as exc:
            click.echo(exc.message, err=True)
            ctx.exit(exc.returncode)

        # Note the current environment state to detect looping on incompatible dependencies.
        try:
            output = subprocess.check_output(['pip', 'freeze'])
            click.echo(output)
        except subprocess.CalledProcessError as exc:
            click.echo(exc.message, err=True)
            ctx.exit(exc.returncode)
        
        if output in previous_freeze:
            # 4b. We detect that we were previously in this state, so we're looping on incompatible dependencies.
            print('OH NO! Looping on incompatible dependencies. Check your dependencies.')
            break

        previous_freeze.append(output)

        # 2. `pip check` to get incompatible dependencies.
        try:
            output = subprocess.check_output(['pip', 'check'])
        except subprocess.CalledProcessError as exc:
            # Error code 1 with no message is the check fail to parse.
            if exc.returncode == 1 and exc.message == '':
                output = exc.output
            else:
                click.echo(exc.message, err=True)
                ctx.exit(exc.returncode)
        reqs_to_fix = re.findall(CHECK_RE, output, flags=re.MULTILINE)
        click.echo(reqs_to_fix)

        # 3. `pip install <missing dependencies>` to fix.
        if not reqs_to_fix:
            # 4a. All dependencies compatible
            print('DONE!')
            break

        for req in sorted(reqs_to_fix):
            try:
                output = subprocess.check_output(['pip', 'install', req])
                click.echo(output)
            except subprocess.CalledProcessError as exc:
                click.echo(exc.message, err=True)
                ctx.exit(exc.returncode)
    else:
        # 4c. Cycled "indefinitely" (10 times) without finding a solution.
        print('OH NO! No solution found after 10 rounds, thats odd. Check your dependencies.')
