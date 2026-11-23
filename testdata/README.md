# Synthetic schema 3 saves
`schema3-synthetic.json.gz` contains one automatically played week per model
from v0.8.6 (Models 1–3) and v0.8.7 (Models 1–4). v0.8.7 source is Git commit
4317e9d. v0.8.6 source is the local verified release. All saves use Galatasaray,
seed 886, the synthetic manager name Compatibility Fixture and a fixed UUID
with integer value 0x886 + model. They use the game's existing catalog.
No personal saves, external game databases, historical application code or
Windows distributions are included.

The tests for actual cross-version engine parity still use the optional older
source directories next to the checkout or its local yedek_v directories.
A missing directory gives an explicit skip. Invalid fixture content or failing
assertions remain test errors.
