# kg4rd visualization

## Add your KGE model

Edit the function `lifespan` in the `main.py` file:

```python
model = ...
model.load_checkpoint(...)
model_repo.add_model(
    model_name='...',
    model=model
)
```

replace the `model` with your own KGE model.

## Run

```bash
uv run src/kg4rd/visualization/backend/main.py
```