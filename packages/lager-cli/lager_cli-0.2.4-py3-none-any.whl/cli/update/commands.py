"""
    lager.update.commands

    Update gateway code on DUTs from GitHub repository
"""
import click
import subprocess
import time
from ..dut_storage import resolve_and_validate_dut, get_dut_user
from ..context import get_default_gateway


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='DUT name or IP to update')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.option('--skip-restart', is_flag=True, help='Skip container restart after update')
@click.option('--branch', default='local-nets', help='Git branch to pull from (default: local-nets)')
def update(ctx, box, dut, yes, skip_restart, branch):
    """
    Update gateway code on a box from GitHub repository

    This command will:
    1. Connect to the gateway via SSH
    2. Ensure udev_rules directory is tracked (sparse checkout)
    3. Pull the latest code from GitHub (git pull)
    4. Install/update udev rules for USB instrument access
    5. Restart Docker containers to apply changes
    6. Verify services are running correctly

    Example:
        lager update --box JUL-3
        lager update --box HYP-3 --yes
    """
    # Use box or dut (box takes precedence)
    resolved = box or dut

    # Use default gateway if no box/dut specified
    if not resolved:
        resolved = get_default_gateway(ctx)

    dut = resolved

    # Resolve DUT name to IP address
    resolved_dut = resolve_and_validate_dut(ctx, dut)

    # Get username (defaults to 'lagerdata' if not specified)
    username = get_dut_user(dut) or 'lagerdata'

    ssh_host = f'{username}@{resolved_dut}'

    # Display update information
    click.echo()
    click.secho('Gateway Update', fg='blue', bold=True)
    click.echo(f'Target:  {dut} ({resolved_dut})')
    click.echo(f'Branch:  {branch}')
    click.echo()

    # Confirm before proceeding
    if not yes:
        if not click.confirm('This will update the gateway code and restart services. Continue?'):
            click.secho('Update cancelled.', fg='yellow')
            ctx.exit(0)

    # Step 1: Check SSH connectivity
    click.echo('Checking connectivity...', nl=False)
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes',
             ssh_host, 'echo test'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho(f'Error: Cannot connect to {ssh_host}', fg='red', err=True)
            click.echo('Please ensure SSH keys are configured correctly.', err=True)
            ctx.exit(1)
        click.secho(' OK', fg='green')
    except subprocess.TimeoutExpired:
        click.secho(' TIMEOUT', fg='red')
        click.secho(f'Error: Connection to {ssh_host} timed out', fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(' FAILED', fg='red')
        click.secho(f'Error: {str(e)}', fg='red', err=True)
        ctx.exit(1)

    # Step 2: Check if gateway directory exists and is a git repo
    click.echo('Checking gateway repository...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'test -d ~/gateway/.git'],
        capture_output=True
    )
    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Gateway directory is not a git repository', fg='red', err=True)
        click.echo()
        click.echo('The gateway may have been deployed with rsync instead of git clone.')
        click.echo('Please re-deploy the gateway using the latest deployment script.')
        ctx.exit(1)
    click.secho(' OK', fg='green')

    # Step 3: Show current version
    click.echo('Current version:', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'cd ~/gateway && git log -1 --format="%h - %s (%cr)"'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        click.echo(f' {result.stdout.strip()}')
    else:
        click.echo(' (unknown)')

    # Step 4: Fetch and check for updates
    click.echo(f'Fetching updates from origin/{branch}...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, f'cd ~/gateway && git fetch origin {branch}'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Failed to fetch updates from GitHub', fg='red', err=True)
        if result.stderr:
            click.echo(result.stderr, err=True)
        click.echo()
        click.echo('This may indicate:')
        click.echo('  - Network connectivity issues')
        click.echo('  - GitHub access problems (check deploy key)')
        click.echo('  - Invalid branch name')
        ctx.exit(1)
    click.secho(' OK', fg='green')

    # Check if there are updates available
    result = subprocess.run(
        ['ssh', ssh_host, f'cd ~/gateway && git rev-list HEAD..origin/{branch} --count'],
        capture_output=True,
        text=True
    )

    needs_pull = False
    if result.returncode == 0:
        commits_behind = int(result.stdout.strip())
        if commits_behind == 0:
            click.secho('✓ Gateway code is already up to date!', fg='green')
            needs_pull = False
        else:
            click.echo(f'Updates available: {commits_behind} new commit(s)')
            needs_pull = True

    if needs_pull:
        # Step 5: Ensure udev_rules is tracked in sparse checkout
        click.echo('Ensuring udev_rules is tracked...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, 'cd ~/gateway && git sparse-checkout list | grep -q "^udev_rules$" || git sparse-checkout add udev_rules'],
            capture_output=True,
            text=True
        )
        # Ignore errors - sparse checkout add is idempotent and may not be needed
        click.secho(' OK', fg='green')

        # Step 6: Checkout the specified branch
        click.echo(f'Checking out branch {branch}...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, f'cd ~/gateway && git checkout {branch}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho(f'Error: Failed to checkout branch {branch}', fg='red', err=True)
            if result.stderr:
                click.echo(result.stderr, err=True)
            ctx.exit(1)
        click.secho(' OK', fg='green')

        # Step 7: Reset to match remote (force pull, handles divergent branches)
        click.echo(f'Updating to match origin/{branch}...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, f'cd ~/gateway && git reset --hard origin/{branch}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho('Error: Failed to update branch', fg='red', err=True)
            if result.stderr:
                click.echo(result.stderr, err=True)

            # Check if it's a sparse checkout issue
            if 'sparse' in result.stderr.lower():
                click.echo()
                click.echo('This may be a sparse checkout configuration issue.')
                click.echo('Try re-deploying the gateway with the latest deployment script.')
            ctx.exit(1)
        click.secho(' OK', fg='green')

        # Show new version
        click.echo('New version:', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, 'cd ~/gateway && git log -1 --format="%h - %s (%cr)"'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f' {result.stdout.strip()}')

    # Step 8: Install udev rules (if they exist)
    click.echo()
    click.echo('Installing udev rules...', nl=False)

    # Check if udev_rules directory exists
    result = subprocess.run(
        ['ssh', ssh_host, 'test -d ~/gateway/udev_rules'],
        capture_output=True
    )

    if result.returncode == 0:
        # Copy udev rules to /tmp, then install with sudo
        install_cmd = (
            'cp ~/gateway/udev_rules/99-instrument.rules /tmp/ && '
            'sudo cp /tmp/99-instrument.rules /etc/udev/rules.d/ && '
            'sudo chmod 644 /etc/udev/rules.d/99-instrument.rules && '
            'sudo udevadm control --reload-rules && '
            'sudo udevadm trigger && '
            'rm /tmp/99-instrument.rules'
        )

        result = subprocess.run(
            ['ssh', ssh_host, install_cmd],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.secho(' OK', fg='green')
        else:
            click.secho(' SKIPPED', fg='yellow')
            if 'password' in result.stderr.lower() or 'sudo' in result.stderr.lower():
                click.echo('  (Passwordless sudo not configured for udev operations)')
                click.echo('  Run deployment script to set up passwordless sudo')
            else:
                click.echo(f'  ({result.stderr.strip()[:50]}...)')
    else:
        click.secho(' SKIPPED (no udev_rules directory)', fg='yellow')

    # Step 8b: Fix sparse checkout nested directory issue
    # Sparse checkout may create gateway/gateway/* structure - copy files to correct location
    click.echo('Checking for sparse checkout nested directories...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         'if [ -d ~/gateway/gateway ]; then '
         '  echo "nested"; '
         'else '
         '  echo "normal"; '
         'fi'],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0 and 'nested' in result.stdout:
        click.secho(' NESTED', fg='yellow')
        click.echo('  Copying files from nested gateway directory...', nl=False)

        # Copy all necessary files from gateway/gateway/* to gateway/*
        copy_result = subprocess.run(
            ['ssh', ssh_host,
             'cd ~/gateway && '
             'cp -rf gateway/python . 2>/dev/null && '
             'cp -rf gateway/controller . 2>/dev/null && '
             'cp -rf gateway/udev_rules . 2>/dev/null && '
             'cp -f gateway/start_all_containers.sh . 2>/dev/null && '
             'cp -f gateway/start_all_containers_hyphen.sh . 2>/dev/null || true'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if copy_result.returncode == 0:
            click.secho(' OK', fg='green')

            # Remove the nested directory after successful copy
            click.echo('  Cleaning up nested directory...', nl=False)
            cleanup_result = subprocess.run(
                ['ssh', ssh_host, 'rm -rf ~/gateway/gateway'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if cleanup_result.returncode == 0:
                click.secho(' OK', fg='green')
            else:
                click.secho(' WARNING', fg='yellow')
                click.echo('  (Could not remove nested directory, but files were copied successfully)')
        else:
            click.secho(' FAILED', fg='red')
            click.secho('Error: Failed to copy files from nested directory', fg='red', err=True)
            if copy_result.stderr:
                click.echo(copy_result.stderr, err=True)
            ctx.exit(1)
    else:
        click.secho(' OK', fg='green')

    # Step 9: Restart containers (unless skipped)
    if skip_restart:
        click.echo()
        click.secho('Skipping container restart (--skip-restart flag set)', fg='yellow')
        click.echo('Run this manually to apply changes:')
        click.echo(f'  ssh {ssh_host} "cd ~/gateway && ./start_all_containers.sh"')
        ctx.exit(0)

    click.echo()
    click.echo('Rebuilding Docker containers (this may take several minutes)...')
    click.echo('  (This will install fresh dependencies like yoctopuce)')

    # Stop and remove existing containers and images
    click.echo('  Stopping containers...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         'cd ~/gateway && '
         'docker stop $(docker ps -aq) 2>/dev/null || true && '
         'docker rm $(docker ps -aq) 2>/dev/null || true && '
         'docker rmi python controller lagerdata/controller 2>/dev/null || true'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        click.secho(' OK', fg='green')
    else:
        click.secho(' WARNING', fg='yellow')

    # Rebuild Python container with --no-cache to ensure fresh dependencies
    click.echo('  Rebuilding Python container (no cache)...')
    click.echo()

    # Stream build output to show progress
    process = subprocess.Popen(
        ['ssh', ssh_host,
         'cd ~/gateway/python && '
         'docker build --no-cache -f docker/gatewaypy3.Dockerfile -t python .'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream output line by line
    if process.stdout:
        for line in process.stdout:
            click.echo(f'    {line}', nl=False)

    return_code = process.wait(timeout=600)

    click.echo()
    if return_code != 0:
        click.secho('  Python container rebuild FAILED', fg='red', bold=True)
        click.secho('Error: Failed to rebuild Python container', fg='red', err=True)
        ctx.exit(1)
    click.secho('  Python container rebuild complete!', fg='green', bold=True)
    click.echo()

    # Rebuild Controller container (can use cache)
    click.echo('  Rebuilding Controller container...')
    click.echo()

    # Stream build output to show progress
    process = subprocess.Popen(
        ['ssh', ssh_host,
         'cd ~/gateway/controller && '
         './build_controller_container.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream output line by line
    if process.stdout:
        for line in process.stdout:
            click.echo(f'    {line}', nl=False)

    return_code = process.wait(timeout=600)

    click.echo()
    if return_code != 0:
        click.secho('  Controller container rebuild FAILED', fg='red', bold=True)
        click.secho('Error: Failed to rebuild Controller container', fg='red', err=True)
        ctx.exit(1)
    click.secho('  Controller container rebuild complete!', fg='green', bold=True)

    # Start containers using the startup script
    click.echo('  Starting containers...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'cd ~/gateway && ./start_all_containers.sh'],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Failed to restart containers', fg='red', err=True)
        if result.stderr:
            click.echo(result.stderr, err=True)
        click.echo()
        click.echo('You may need to manually restart containers:')
        click.echo(f'  ssh {ssh_host}')
        click.echo('  cd ~/gateway && ./start_all_containers.sh')
        ctx.exit(1)

    click.secho(' OK', fg='green')

    # Step 10: Wait for containers to stabilize
    click.echo('Waiting for services to start...', nl=False)
    time.sleep(5)
    click.secho(' OK', fg='green')

    # Step 11: Verify containers are running
    click.echo('Verifying container status...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         "docker ps --filter 'name=controller' --filter 'name=python' --format '{{.Names}}' | wc -l"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        running_count = int(result.stdout.strip())
        if running_count >= 2:
            click.secho(' OK', fg='green')
        else:
            click.secho(f' WARNING (only {running_count}/2 containers running)', fg='yellow')
    else:
        click.secho(' FAILED', fg='red')

    # Show final status
    click.echo()
    click.secho('Container Status:', fg='blue', bold=True)
    result = subprocess.run(
        ['ssh', ssh_host,
         "docker ps --filter 'name=controller' --filter 'name=python' "
         "--format 'table {{.Names}}\t{{.Status}}'"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        click.echo(result.stdout.strip())

    # Final success message
    click.echo()
    click.secho('✓ Gateway update completed successfully!', fg='green', bold=True)
    click.echo()
    click.echo('You can verify connectivity with:')
    click.echo(f'  lager hello --dut {dut}')
    click.echo()
