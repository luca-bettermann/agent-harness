# Only an operator ruling or physical safety may add a gate

A gate is any condition that refuses a start, stops a run, drops data or marks a device not ready. Agents tended to add such stops for missing or unproven input, which blocked work without catching defects. Now only an operator ruling cited in the commit, or physical safety at the device owner, may add one; everything else is reported as a warning or an incomplete record, and `code-review` returns unruled gates.
