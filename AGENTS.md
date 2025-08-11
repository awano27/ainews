# Repository Guidelines

## Project Structure & Module Organization
- Source lives in `src/`; tests in `tests/`; scripts in `scripts/`.
- Keep assets in `assets/` and docs in `docs/`. Example paths: `src/module_name/`, `tests/test_module_name.py` or `tests/module_name.test.ts`.
- Prefer small, focused modules. Group related code by feature, not by layer only.

## Build, Test, and Development Commands
- Install deps: `npm ci` (Node), `pip install -e .[dev]` (Python), or `cargo build` (Rust).
- Run locally: `npm run dev`, `python -m src.main`, or `cargo run` as applicable.
- Build: `npm run build`, `python -m build`, or `cargo build --release`.
- Test: `npm test`, `pytest -q`, or `cargo test`.
- If a `Makefile` exists, prefer `make setup`, `make test`, `make lint` for consistency.
 - Daily page: `python scripts/generate_daily.py`（JSTの本日版を生成し、`docs/index.html` を更新）。
   - 任意: `--date YYYY-MM-DD` 指定、`--force` で上書き。

## Automation (GitHub Actions)
- Workflow: `.github/workflows/publish-daily.yml`（毎日 13:00 JST に実行）。
- 動作: テンプレから当日ページを生成し、`docs` の差分があれば自動コミット/プッシュ。
- 手動実行: リポジトリの Actions → Publish Daily AI News → Run workflow。
- 前提: GitHub Pages を Branch=`main`, Folder=`/docs` で有効化。

## Coding Style & Naming Conventions
- Indentation: 2 spaces for JS/TS; 4 spaces for Python; Rust uses `rustfmt` defaults.
- Naming: `snake_case` for files and Python; `camelCase` for variables/functions in JS/TS; `PascalCase` for classes/types.
- Formatters/Linters: `prettier` + `eslint` (JS/TS), `black` + `ruff` (Python), `rustfmt` + `clippy` (Rust).
- Keep functions < 50 lines; prefer pure functions and clear interfaces.

## Testing Guidelines
- Place tests mirroring source paths under `tests/`.
- Naming: `test_<unit>.py` (pytest), `<unit>.test.ts`/`.spec.ts` (Jest), or module tests in Rust.
- Aim for >80% coverage on core logic. Run locally with `npm test`, `pytest`, or `cargo test` before pushing.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Commits: small, scoped, and imperative mood. Example: `fix(api): handle empty payload`.
- PRs: include summary, rationale, screenshots/logs when UI/CLI changes, and link related issues (`Closes #123`). Ensure tests and linters pass.

## Security & Configuration Tips
- Never commit secrets. Use `.env.local` and document required vars in `docs/config.md`.
- Validate and sanitize all inputs. Add schema checks where applicable.
- Enable pre-commit hooks for format/lint/test if available (`pre-commit install` or `npm run prepare`).
