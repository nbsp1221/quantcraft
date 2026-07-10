# Candidate Search In Validation

Standalone `ParameterStudy` is no longer the current public research API.
Quantcraft's beta research layer now treats finite parameter search as an
internal part of validation flows such as `WalkForwardValidation`.

Use `WalkForwardValidation` when a small parameter grid should be selected on
train windows and challenged on unseen OOS windows:

```python
from quantcraft.research import RollingSplitPolicy, WalkForwardValidation

validation = WalkForwardValidation(
    engine=engine,
    bars=bars,
    strategy=ParameterizedSmaStrategy,
    split_policy=RollingSplitPolicy(train_size=120, test_size=30),
    objective=("returns.total_return", "max"),
)

result = validation.run(
    parameters={"fast": [2, 3], "slow": [3, 4]},
    constraint=lambda config: config["fast"] < config["slow"],
)

candidate_records = result.to_candidate_records()
fold_records = result.to_records()
```

Candidate search remains a research diagnostic. It is not an optimizer guarantee
or a trading recommendation. The public contract is the validation result,
including records, diagnostics, artifacts, and provenance.
