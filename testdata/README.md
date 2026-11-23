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

Set `TOP_ANTRENORU_TEST_ARCHIVE` to the absolute path of a local source
archive to run all historical comparisons without moving the checkout.
Place the version directories directly under that path:

- `yedek_v0.5.5`, `yedek_v0.6.0`, `yedek_v0.7.0`, `yedek_v0.7.5`, `yedek_v0.7.7`,
  `yedek_v0.7.8`, `yedek_v0.7.9`, `yedek_v0.7.9.1`, `yedek_v0.7.9.2`,
  `yedek_v0.7.9.3`, `yedek_v0.8.0`
- `top ant tester v0.8.1`, `top ant v0.8.3`, `top ant v0.8.4`,
  `top ant v0.8.5`, `top ant v0.8.6`

Historical tests need the game source and game JSON files. They create
careers at runtime. If the archive path is set, a missing version fails
the test. Keep personal saves, game executables and external databases out
of the fixture directory.
