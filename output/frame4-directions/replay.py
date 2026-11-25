"""Replay the frozen frame-four experiment using the production cut benchmark."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

study = Path(__file__).resolve().parent
bench = study.parents[1]/'benchmark/heldout-cut/replay.py'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shot', required=True, choices=['blind','original'])
args, options = parser.parse_known_args()
for line in (study/'freeze.sha256').read_text().splitlines():
    digest, filename = line.split()
    assert hashlib.sha256((study/filename).read_bytes()).hexdigest() == digest
subprocess.run([sys.executable, str(bench), '--shot', str(study/(args.shot+'.json')),
                '--patch', str(study/'candidate.patch'), '--out', str(study/args.shot),
                '--clip-label', 'Challenger  ·  frame 4 ray directions', *options], check=True)
