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
  "security": {
    "classification": "security-sensitive",
    "surfaces": ["authentication/session/token"],
    "trust_boundaries": ["refresh token -> session renewal"],
    "abuse_cases": ["replay revoked refresh token"],
    "controls": ["rotation", "revocation", "authorization boundary", "sensitive-token logging protection"],
    "evidence": [],
    "head_sha": null,
    "limitations": [],
    "candidate_disposition": null
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Marker trùng hoặc lệch cặp là invalid. Task schema v1 phải rebuild thành v2 từ GitHub state hiện tại trước khi tiếp tục bình thường.

### Frontend state tùy chọn

Task frontend vẫn dùng manifest v2 và workflow hiện tại. Chỉ task thực sự chạm UI mới thêm block `frontend` tùy chọn:

```json
{
  "frontend": {
    "surface": "application",
    "intent": "refine",
    "design_context": {
      "path": null,
      "mode": "infer-existing-ui"
    },
    "acceptance_dimensions": [
      "visual-consistency",
      "responsive-behavior",
      "accessibility"
    ],
    "acceptance_map": {
      "visual-consistency": ["AC1"],
      "responsive-behavior": ["AC2"],
      "accessibility": ["AC3"]
    },
    "visual_qa": {
      "max_rounds": 2,
      "browser_tooling": [],
      "evidence": [],
      "head_sha": null,
      "limitations": []
    }
  }
}
```

Classifier được giữ bảo thủ: chỉ có React/Next/Vue... trong project chưa đủ để coi task là frontend; request hoặc target phải thật sự chạm UI. `DESIGN.md` là optional; nếu không có, agent suy ra visual system hiện tại từ bounded UI code. Frontend verification tái sử dụng tooling sẵn có của project, không tự cài browser runtime chỉ vì policy này. Visual evidence đã ghi phải gắn với PR head hiện tại; nếu thiếu visual tooling thì ghi rõ limitation.

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

Chỉ high-confidence identifiers được lưu vào `context.symbols`; không cache source trong manifest. Retrieval runtime có diagnostics cho path được chọn, score, round và lý do từ request/symbol. `max_search_rounds` và `max_symbol_hints` được dùng thật; khi scan bị giới hạn, path nông được ưu tiên trước subtree sâu.

## Modes

- `feature` — project/chức năng mới
- `change` — thay đổi behavior/compatibility có chủ đích
- `bug_fix` — sửa defect
- `refactor` — đổi cấu trúc, giữ behavior
- `hotfix` — fix production tối thiểu, khẩn cấp
- `test` — test/coverage, mặc định không đổi production behavior
- `docs` — README/docs/examples/metadata, chỉ đọc code tối thiểu để verify nội dung

## Behavioral Coding Policy

Kit áp dụng một behavioral policy xuyên suốt plan, build, verify và GitHub review:

- **Think before coding:** nêu rõ assumption và tradeoff có ảnh hưởng thực tế. Chỉ hỏi khi ambiguity có thể đổi behavior, contract, dữ liệu, security, compatibility, destructive effect hoặc scope; ambiguity nhỏ, reversible có thể tiếp tục với assumption bảo thủ được nói rõ.
- **Simplicity first:** viết lượng code tối thiểu cần thiết cho behavior đã chấp nhận. Tránh feature suy đoán, abstraction chỉ dùng một lần và configurability không được yêu cầu. Defensive branch chỉ xử lý trạng thái thực sự có thể xảy ra theo contract đã biết, không thêm case “bất khả thi” do agent tự tưởng tượng.
- **Surgical changes:** không tự ý refactor, rename, reformat, cleanup hoặc xóa code không liên quan. Cleanup chỉ áp dụng cho artifact trở nên thừa do chính patch hiện tại.
- **Goal-driven execution:** map các bước không-trivial với verification evidence quan sát được. Bug ưu tiên reproduce -> root cause -> regression -> minimal fix -> verify; refactor xác nhận behavior trước và sau.
- **Changed-line traceability:** mỗi dòng thay đổi phải truy được về request, acceptance criterion, regression/compatibility/security evidence bắt buộc, hoặc cleanup do thay đổi này tạo ra.

Các rule này ưu tiên diff nhỏ, dễ review nhưng không ép agent hỏi lại đối với quyết định low-risk và reversible.

## Comment & Documentation Policy

Kit ưu tiên code tự giải thích bằng tên và cấu trúc. Comment dùng để giữ thông tin mà code không thể hiện rõ: **WHY**, constraint, invariant, tradeoff không hiển nhiên, security assumption, reasoning về performance/cache, edge case khó và workaround có chủ đích. Tránh comment kể lại code hiển nhiên hoặc docstring boilerplate cho private helper đơn giản. Public/shared contract nên được document khi caller cần biết behavior, error, side effect, lifecycle hoặc invariant. Comment/docstring/docs bị stale trong vùng sửa phải được cập nhật/xóa; TODO/FIXME phải actionable.

## Security Policy

Kit **không** đảm bảo code được tạo/sửa là an toàn tuyệt đối. Rule có thể audit là:

> **Security-sensitive changes cannot silently pass without explicit security review/evidence.**

```text
PLAN
  ↓
identify security-sensitive surface
  ↓
BUILD
  ↓
secure coding rules
  ↓
VERIFY
  ├─ security diff review
  ├─ project-native security scanner nếu có
  ├─ dependency vulnerability check khi phù hợp/có sẵn
  └─ targeted security tests
  ↓
GITHUB REVIEW
  └─ bắt buộc security evidence của current head
```

Authentication, authorization, session/token/password, upload/filesystem, database query với dữ liệu user kiểm soát, URL do user kiểm soát, HTML/template rendering, command execution, payment/webhook và secrets/credentials tự động làm task thành `security-sensitive` khi request hoặc impact/diff cuối cùng chạm tới chúng.

Task manifest mới lưu object `security` gồm classification, surfaces, trust boundaries, abuse cases, controls, structured evidence, evidence head SHA và limitations. Manifest schema-v2 cũ chưa có `security` vẫn hợp lệ để backward-compatible; task security-sensitive đang active phải bổ sung block trước verify.

Với task security-sensitive, lint/type/test/build hoặc runtime `PASS_VERIFIED` thông thường **chưa đủ**. Security evidence phải explicit và bind đúng current PR head. Runtime tạo candidate bảo thủ từ request/path/symbol; nếu review vẫn giữ task là `standard`, `security.candidate_disposition` phải giải thích rõ lý do. Scanner thiếu phải được ghi thành limitation, không được âm thầm coi là success.

## Completion gate

`PASS_VERIFIED` chỉ hợp lệ khi mọi acceptance criterion đều `met` và có structured evidence. `ready` và `complete` cần current pass. Gate có config còn kiểm tra `verification.require_commands`, security-candidate disposition, frontend acceptance mapping và evidence frontend/security đúng current head. Khi head đổi, mọi verification outcome cũ bị clear và task từng ready/complete quay lại trạng thái verifying.

```bash
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
```

Config v2 giờ là strict contract và có JSON Schema riêng. CI validate template task/project/config bằng Draft 2020-12 JSON Schema ngoài runtime validator.

## Bootstrap

Local:

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

Installer giữ nguyên `AGENTS.md` có sẵn, tạo `.vibe` contract và detect stack nhẹ từ manifest/file phổ biến. Verification detection tôn trọng npm/pnpm/yarn/bun theo metadata/lockfile và không còn tự suy ra pytest chỉ vì có thư mục Python `tests/`. Hỗ trợ heuristic cho Python/FastAPI/Django/Flask, JS/TS/Next/React/Vue/Nuxt/Svelte/Vite/Nest/Express, Ruby/Rails, PHP/WordPress/Laravel, Go/Rust/Java và các verification command đã có.

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
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
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
