import subprocess
from subprocess import PIPE

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
    ['git', 'rev-list', '--count', 'HEAD'], stdout=PIPE, stderr=PIPE).stdout)

VERSION = f"{BRANCH}@{COMMIT_ID}@{NUM_COMMITS}"
