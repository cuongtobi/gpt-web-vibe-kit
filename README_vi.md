# gpt-web-vibe-kit

[Hướng dẫn sử dụng chi tiết](docs/usage-vi.md) · [English guide](docs/usage.md) · [PR task contract](docs/pr-task-contract.md)

Bộ vibe-coding GitHub-native cho **ChatGPT Web + GitHub**, tối ưu cho project cá nhân vừa và nhỏ, không cần local checkout bền vững hay backend context riêng.

```text
session -> plan -> build -> verify -> github-review
```

## Mục tiêu thiết kế

- GitHub là durable state; session mới không phụ thuộc chat cũ.
- Chỉ load **bounded context** liên quan, không quét/load toàn repo.
- Mỗi task dùng một PR nên nhiều task có thể chạy song song.
- Retrieval nhẹ, có symbol-awareness, thực hiện bằng vài vòng GitHub search có giới hạn.
- Verification chỉ hợp lệ cho đúng current PR head SHA.
- Không cần vector DB, daemon, LSP server, graph DB hay external backend.

## State model

Project state ổn định:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
```

Task state:

```text
một pull request
├── branch/head SHA
├── đúng một task manifest schema v2
├── current diff
├── CI/checks
└── review discussion
```

Source luôn fetch mới từ GitHub hiện tại.

## Manifest v2

Mỗi PR do kit quản lý phải có **đúng một** block:

```text
<!-- gpt-web-vibe:task:start -->
```json
{
  "schema_version": 2,
  "task_id": "jwt-refresh",
  "mode": "bug_fix",
  "status": "building",
  "request": "Fix refresh token after session expiry",
  "base_branch": "main",
  "base_sha": "<base-sha>",
  "head_branch": "vibe/bug_fix/jwt-refresh",
  "head_sha": "<head-sha>",
  "targets": ["app/services/auth.py"],
  "context": {
    "symbols": ["refresh_access_token"],
    "dependencies": ["app/security/token.py"],
    "consumers": ["app/api/auth.py"],
    "tests": ["tests/test_auth.py"],
    "config_files": [],
    "observed_files": [
      {
        "path": "app/services/auth.py",
        "sha": "<github-blob-sha>",
        "role": "target",
        "depth": 0,
        "symbols": ["refresh_access_token"]
      }
    ]
  },
  "acceptance": [
    {
      "id": "AC1",
      "expected": "Expired access can be refreshed with a valid refresh token.",
      "status": "pending",
      "evidence": []
    }
  ],
  "verification": {
    "commands": ["pytest tests/test_auth.py"],
    "head_sha": null,
    "ci_run_id": null,
    "status": null
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Marker trùng hoặc lệch cặp là invalid. Task schema v1 phải rebuild thành v2 từ GitHub state hiện tại trước khi tiếp tục bình thường.

## Hard context budget

`.vibe/config.json` chứa giới hạn bắt buộc:

```json
{
  "context": {
    "max_dependency_depth": 2,
    "max_source_files": 15,
    "max_test_files": 6,
    "max_related_modules": 6,
    "rebuild_changed_ratio": 0.5,
    "max_search_rounds": 3,
    "max_symbol_hints": 24
  }
}
```

Mỗi observed file lưu `role`, `depth`, `symbols`, `sha`, nên runtime có thể kiểm tra budget thật. Nếu task không thể fit an toàn, phải giảm/chia scope thay vì đọc thêm vô hạn.

## Restore session mới

```text
AGENTS.md
-> .vibe/config.json
-> .vibe/project-context.json
-> PR được chọn
-> strict manifest v2
-> current diff
-> current blob SHA
-> budget check
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> bounded current files
-> current-head CI
```

- `CONTEXT_HIT`: observed references không đổi và vẫn trong budget.
- `CONTEXT_REFRESH`: chỉ một subset nhỏ thay đổi.
- `CONTEXT_REBUILD`: scope/baseline đổi, manifest invalid/stale, quá nhiều file đổi hoặc context vượt budget.

## Iterative symbol-aware retrieval

`plan` tìm context theo các vòng có giới hạn:

```text
request/error/route keywords
-> promising files
-> symbols liên quan
-> search symbol/import
-> direct dependencies/consumers/tests
-> dừng theo budget
```

Chỉ high-confidence identifiers được lưu vào `context.symbols`; không cache source trong manifest.

## Modes

- `feature` — project/chức năng mới
- `change` — thay đổi behavior/compatibility có chủ đích
- `bug_fix` — sửa defect
- `refactor` — đổi cấu trúc, giữ behavior
- `hotfix` — fix production tối thiểu, khẩn cấp
- `test` — test/coverage, mặc định không đổi production behavior
- `docs` — README/docs/examples/metadata, chỉ đọc code tối thiểu để verify nội dung

## Bootstrap

Local:

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

Installer giữ nguyên `AGENTS.md` có sẵn, tạo `.vibe` contract và detect stack nhẹ từ manifest/file phổ biến. Hỗ trợ heuristic cho Python/FastAPI/Django/Flask, JS/TS/Next/React/Vue/Nuxt/Svelte/Vite/Nest/Express, Ruby/Rails, PHP/WordPress/Laravel, Go/Rust/Java và các verification command đã có.

Trên ChatGPT Web, dùng `skills/bootstrap/SKILL.md` để tạo contract tương tự trực tiếp qua GitHub.

## Cách dùng trên ChatGPT Web

Task mới:

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit và chạy full vibe workflow.

Task:
Fix refresh-token rotation sau khi session hết hạn.
```

Session mới:

```text
@GitHub tiếp tục PR #42 trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore context từ schema-v2 PR manifest rồi tiếp tục.
```

Test-only:

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Thêm regression tests cho <module>. Dùng mode test và không đổi production behavior.
```

Docs-only:

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Cập nhật <docs>. Dùng mode docs và chỉ đọc source cần thiết để kiểm chứng nội dung.
```

Xem [docs/usage-vi.md](docs/usage-vi.md) cho toàn bộ trường hợp sử dụng.

## Verification

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

PASS chỉ hợp lệ khi:

```text
verification.head_sha == task.head_sha == current PR head SHA
```

Head thay đổi thì PASS cũ tự trở thành stale evidence.

## Runtime helpers

```bash
python runtime/vibe_web.py validate-config .vibe/config.json
python runtime/vibe_web.py validate-project .vibe/project-context.json
python runtime/vibe_web.py validate-task task.json --config .vibe/config.json
python runtime/vibe_web.py validate-pr-body pr-body.md --config .vibe/config.json
python runtime/vibe_web.py budget-status task.json --config .vibe/config.json
python runtime/vibe_web.py context-status task.json current-shas.json --config .vibe/config.json
python runtime/vibe_web.py detect-project /path/to/project
```

Runtime vẫn chỉ dùng Python standard library.

## Tests

```bash
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/retrieval.py runtime/vibe_web.py
```

Repo có ba integration fixture nhỏ cho FastAPI, Next.js và Rails, cùng regression tests cho HIT/REFRESH/REBUILD, duplicate manifest, hard budget và current-head verification.
