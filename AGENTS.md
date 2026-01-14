# Repository Guidelines

## Project Structure & Module Organization
- `qa/`: Chat flow and G-code interaction logic.
- `lang_chain/`: LLM client, retrievers, and helpers.
- `model/`: Graph/RAG models, preload, search services.
- `web/api/`: FastAPI routes; register in `web/api/api.py` and `web/api/manage.py`.
- `config/`: `config-<env>.yaml` files loaded via `PY_ENVIRONMENT`.
- `tests/`: Test scripts and demos. Also see `run_algorithm_tests.sh`.
- `asset/`, `data/`, `resource/`, `templates/`, `logs/`: static assets, datasets, UI resources, Jinja/Gradio templates, logs.

## Build, Test, and Development Commands
- Install deps: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- All-in-one (API + WebUI): `python app.py`.
- API only: `PY_ENVIRONMENT=local python api_backend.py`.
- WebUI only: `PY_ENVIRONMENT=local python webui.py`.
- Run all tests (unittest): `python -m unittest discover -s tests -p 'test*.py' -v`.
- Algorithm demos: `bash ./run_algorithm_tests.sh`.

## Coding Style & Naming Conventions
- Python, PEP 8, 4-space indentation. Use `snake_case` for functions/variables, `CamelCase` for classes.
- Organize domain logic in `qa/`; retrieval/model code in `lang_chain/` and `model/`; API endpoints in `web/api/`.
- Add type hints and short docstrings for public functions. Keep modules small and cohesive.
- Logging: use `logger.Logger` (writes to `logs/` with rotation/retention).

## Testing Guidelines
- Prefer `unittest`; place files under `tests/` named `test_<feature>.py`.
- Keep tests deterministic; avoid network/API keys. Mock I/O where practical.
- Run a single file: `python tests/test_<name>.py`.
- For UI/flow checks, see examples in `tests/` (e.g., `test_gcode_generation.py`).

## Commit & Pull Request Guidelines
- Commits: imperative, concise; English or Chinese acceptable.
  - Examples: `Refactor: unify parameter parsing`, `修复: G代码验证边界条件`.
- PRs: clear description, scope, and rationale; link issues; include screenshots for UI changes and run steps (`PY_ENVIRONMENT=local`, ports used).

## Security & Configuration Tips
- Secrets live in `.env` (e.g., `ZHIPUAI_API_KEY`). Do not commit real keys.
- Select config via `PY_ENVIRONMENT` (e.g., `local` → `config/config-local.yaml`).
- Default ports from config: API `18881`, WebUI `7860`. Adjust in `config/config-<env>.yaml`.

