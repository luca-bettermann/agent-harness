## Our additions

- **One harness per boundary:** each boundary has one shared test harness, built from the real code on both sides and reused by every test that crosses it. A side that can't run in a test is a minimal fake of its published contract.
- **Smallest real input:** use the smallest real input that still shows the failure the test is about. Test jobs use the smallest real inputs; none runs a full-scale dataset.
- **Tests earn their cost:** a test stays only when its benefit clearly exceeds its cost in code and run time. A job over the INSTANCE time budget gets smaller inputs, never a longer timeout.
- **Golden files** change only through a ruled regeneration that names the fields allowed to differ; everything else must still match.
