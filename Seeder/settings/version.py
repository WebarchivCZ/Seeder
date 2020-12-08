import subprocess
from subprocess import PIPE

try:
    # git rev-parse --abbrev-ref HEAD
    BRANCH = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        stdout=PIPE, stderr=PIPE).stdout.decode('utf-8').strip()
    # git rev-parse --short HEAD
    COMMIT_ID = subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'],
        stdout=PIPE, stderr=PIPE).stdout.decode('utf-8').strip()
    # git rev-list --count HEAD
    NUM_COMMITS = int(subprocess.run(
        ['git', 'rev-list', '--count', 'HEAD'],
        stdout=PIPE, stderr=PIPE).stdout)
    
    VERSION = f"{BRANCH}@{COMMIT_ID}@{NUM_COMMITS}"
    
    # git log -1 --date=format:"%Y/%m/%d %T" --format="%ad"
    VERSION_DATETIME = subprocess.run(
        ['git', 'log', '-1', '--date=format:"%d. %m. %Y %T"', '--format="%ad"'],
        stdout=PIPE, stderr=PIPE).stdout.decode('utf-8').strip(
    ).replace('"', '')

except:
    VERSION = "Version cannot be loaded"
    VERSION_DATETIME = "Commit datetime cannot be loaded"
