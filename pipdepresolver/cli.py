import subprocess
import re

import click


CHECK_RE = r'^.* has requirement (?P<req>[^,]+), but you have .*$'


@click.group()
def cli():
    pass


@cli.command('install')
@click.argument('src_file', type=click.Path(exists=True, allow_dash=True))
@click.pass_context
def install(ctx, src_file):

    # 1. Run a first `pip install -r src_file`.
    try:
        output = subprocess.check_output(['pip', 'install', '-r', src_file])
        click.echo(output)
    except subprocess.CalledProcessError as exc:
        click.echo(exc.message, err=True)
        ctx.exit(exc.returncode)

    # 2. Get in a cycle of `pip check` & `pip install <reqs>`.
    for _ in range(10):  # Max 10 rounds.
        # 2.1. `pip check` to get incompatible dependencies.
        try:
            output = subprocess.check_output(['pip', 'check'])
        except subprocess.CalledProcessError as exc:
            # Error code 1 with no message is the check fail to parse.
            if exc.returncode == 1 and exc.message == '':
                output = exc.output
            else:
                click.echo(exc.message, err=True)
                ctx.exit(exc.returncode)

        # 2.2 `pip install <missing dependencies>` to fix.
        reqs = re.findall(CHECK_RE, output, flags=re.MULTILINE)
        if reqs:
            try:
                output = subprocess.check_output(['pip', 'install', ' '.join(reqs)])
                click.echo(output)
            except subprocess.CalledProcessError as exc:
                click.echo(exc.message, err=True)
                ctx.exit(exc.returncode)
        else:
            # 2.3 All dependencies compatible
            print('DONE!')
            break
    else:
        # 2.4 Cycled indefinitely without finding a solution.
        print('OH NO! No solution found. Check your dependencies.')
