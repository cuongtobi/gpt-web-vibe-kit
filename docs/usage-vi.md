# Hướng dẫn sử dụng gpt-web-vibe-kit

Tài liệu này mô tả đầy đủ cách dùng `gpt-web-vibe-kit` trên **ChatGPT Web + GitHub** cho project cá nhân vừa và nhỏ.

Kit không cần daemon local, vector database, persistent checkout, LSP server hay backend context riêng.

Workflow chuẩn:

```text
session -> plan -> build -> verify -> github-review
```

Durable state nằm trong repository và task PR, không nằm trong chat history.

---

## 1. Bootstrap repository lần đầu

Prompt:

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit.
Đọc skills/bootstrap/SKILL.md và bootstrap repo này.

Giữ nguyên AGENTS.md nếu đã có.
Detect stack, framework, entrypoint và verification command hiện có.
```

Bootstrap tạo/cập nhật:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
.vibe/README.md
```

Project context chỉ chứa routing metadata nhỏ, không cache source.

### Bootstrap local

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

Installer local dùng heuristic nhẹ từ manifest/file phổ biến.

---

## 2. Session mới đọc gì

Thứ tự restore chuẩn:

```text
AGENTS.md
-> .vibe/config.json
-> .vibe/project-context.json
-> PR được chọn
-> đúng một schema-v2 task manifest
-> current diff
-> compare observed blob SHA
-> hard-budget check
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> bounded current files
-> current-head CI/reviews
```

Không dùng việc paste lại chat cũ làm cơ chế continuation chính.

---

## 3. Hard context budget

Các giá trị trong `.vibe/config.json` là giới hạn bắt buộc.

Mặc định v2:

```json
{
  "max_dependency_depth": 2,
  "max_source_files": 15,
  "max_test_files": 6,
  "max_related_modules": 6,
  "rebuild_changed_ratio": 0.5,
  "max_search_rounds": 3,
  "max_symbol_hints": 24
}
```

Nếu task không fit an toàn:

1. giảm scope;
2. chia task/PR;
3. không load code không liên quan.

Không bypass budget chỉ để hoàn tất task.

---

## 4. Iterative symbol-aware retrieval

`plan` search GitHub theo các vòng có giới hạn.

### Vòng 1: direct evidence

Search:

- error/trace text;
- route/endpoint;
- config key;
- identifier user cung cấp;
- keyword mạnh từ task.

### Vòng 2: symbols

Chỉ đọc candidate hứa hẹn, sau đó lấy các identifier liên quan:

- function;
- class;
- type/interface;
- constant;
- module/import specifier.

Lưu high-confidence identifier vào `context.symbols`, rồi search tiếp các symbol này.

### Vòng 3: direct neighborhood

Search:

- dependency/import/require;
- consumer/usage;
- test;
- config/schema/API/framework registration.

Dừng sớm nếu target và neighborhood cần thiết đã rõ.

Một search rỗng không chứng minh rằng không có impact.

---

## 5. Build project mới

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Build một <mô tả project>.

Yêu cầu:
- ...
- ...

Chạy full vibe workflow.
```

Flow:

```text
requirements
-> bootstrap contract
-> architecture/stack
-> branch + PR + schema-v2 manifest
-> implementation
-> tests/config/docs
-> current-head verification
-> review
```

Mode: `feature`.

---

## 6. Thêm chức năng mới

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Thêm <feature>.

Yêu cầu:
- giữ <contract>;
- có focused tests;
- không thêm dependency nếu không cần.

Chạy full workflow.
```

Context:

```text
request
-> exact target
-> public/data/config contracts
-> direct dependencies
-> direct consumers
-> tests
```

Mode: `feature`.

---

## 7. Thay đổi behavior hiện có

Dùng mode `change`.

Plan:

```text
current behavior
-> desired behavior
-> compatibility
-> affected consumers/contracts
-> tests
```

Chú ý API, config, persisted schema, serialized data và backward compatibility.

---

## 8. Fix bug

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>.

Bắt buộc:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

Flow:

```text
symptom/error
-> candidate files
-> relevant symbols
-> target/root cause
-> regression test
-> minimal fix
-> affected tests
-> current-head verification
```

Mode: `bug_fix`.

Không sửa dựa trên root-cause guess chưa có evidence.

---

## 9. Hotfix production

Dùng `hotfix`.

Rule:

- patch nhỏ nhất an toàn;
- không cleanup tiện tay;
- không rename/refactor ngoài scope;
- không upgrade dependency nếu fault không yêu cầu;
- thêm regression coverage khi khả thi;
- verify current head trước khi hoàn tất.

---

## 10. Test-only

Dùng mode `test`.

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Thêm test cho <module/behavior>.

Cover:
- happy path;
- invalid input;
- important errors;
- regression edge cases.

Dùng mode test.
Không đổi production behavior nếu tôi không yêu cầu.
```

Context:

```text
production target
-> current behavior/contract
-> existing test harness/helpers
-> relevant edge cases
```

Nếu test phát hiện bug production ngoài scope, báo lại thay vì âm thầm sửa.

---

## 11. Tăng coverage

Vẫn dùng `test`.

Ưu tiên:

1. business-critical behavior;
2. security/error boundaries;
3. regressions;
4. branching phức tạp.

Không viết test vô nghĩa chỉ để tăng phần trăm.

---

## 12. Docs-only

Dùng mode `docs`.

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Cập nhật:
<README/docs/API guide>.

Dùng mode docs.
Chỉ đọc source/config cần thiết để verify nội dung.
Không refactor code ngoài scope.
```

Context:

```text
documentation target
-> source/config chứng minh claim
-> examples/links
-> docs checks/CI
```

Mode này tránh dependency expansion không cần thiết.

---

## 13. Refactor function/class/module

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Refactor <target>.
Giữ nguyên behavior và public contract.

Trước khi sửa:
- tìm direct dependencies;
- tìm toàn bộ direct consumers hợp lý có thể discover;
- capture baseline test/behavior;
- ghi invariants.

Sau khi sửa:
- search old references;
- chạy affected checks;
- verify current head.
```

Mode: `refactor`.

Flow:

```text
target symbol
-> direct dependencies
-> direct consumers
-> tests/contracts
-> baseline
-> refactor
-> old-reference search
-> verify unchanged behavior
```

---

## 14. Refactor lớn

Không bypass context limit. Nếu quá rộng thì chia PR.

Ví dụ:

```text
PR1: introduce boundary
PR2: migrate consumers
PR3: remove old implementation
```

Mỗi PR có manifest v2 và verification riêng.

---

## 15. Rename symbol/module/API

Xử lý như `refactor`.

Search:

- symbol usages;
- imports/requires;
- string/config/registry reference;
- framework wiring;
- public docs;
- tests.

Sau sửa phải search lại old symbol/path.

---

## 16. Thêm API endpoint

Context thường:

```text
route/controller
-> request/response schema
-> service/use-case
-> repository/data boundary
-> auth/middleware
-> tests
```

Persist route/service/schema symbols nếu chúng hữu ích cho continuation.

---

## 17. Database/schema migration

Chỉ inspect neighborhood liên quan:

- model/schema;
- migration;
- serializer/DTO/API contract;
- affected query;
- existing-data compatibility;
- tests.

Acceptance nên bao gồm behavior với existing data nếu có.

---

## 18. Thêm package

Trước khi thêm dependency:

- kiểm tra repo đã có capability tương đương chưa;
- giải thích vì sao cần;
- kiểm tra compatibility;
- update lockfile;
- chạy test/build liên quan;
- document config mới có ý nghĩa.

Mode thường `feature` hoặc `change`.

---

## 19. Upgrade dependency/framework

Dùng `change`.

Chỉ phân tích breaking change liên quan repo hiện tại, lập bounded impact map rồi chạy affected checks đủ rộng.

---

## 20. Frontend feature

Context:

```text
route/page
-> component
-> hook/composable/store
-> API/data layer
-> tests
```

Với Next.js/Nuxt/SvelteKit, kiểm tra server/client boundary và file-system routing.

---

## 21. Frontend bug

Không mặc định component đang hiển thị lỗi là root cause. Search state/cache/data-flow symbols và direct consumers.

Các vùng hay gặp:

- query cache invalidation;
- store;
- mutation;
- stale props;
- server/client boundary.

---

## 22. WordPress theme/plugin

Không sửa WordPress core.

Inspect:

- hooks/filters;
- REST registration;
- shortcodes/blocks;
- options/meta;
- templates;
- enqueue behavior.

Hook composition động chỉ là static-best-effort; verify bằng native checks/manual integration khi cần.

---

## 23. Rails/Laravel/Django/Nest và framework magic

Không chỉ dựa static imports. Dùng adapter hints và inspect routes, DI/providers, callbacks, autoloading/registry cùng native tests.

---

## 24. Plan only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

CHỈ PLAN. Không sửa code.

Task:
<mô tả>
```

Chạy:

```text
session -> plan
```

Manifest có thể giữ status `planning`.

---

## Behavioral Coding Policy

Áp dụng các rule sau xuyên suốt task:

- nêu rõ material assumption/tradeoff trước implementation;
- chỉ hỏi khi ambiguity có thể làm thay đổi behavior, contract, dữ liệu, security, compatibility, destructive effect hoặc scope;
- với ambiguity nhỏ/reversible, nêu assumption bảo thủ rồi tiếp tục;
- ưu tiên implementation đơn giản nhất thỏa acceptance criteria;
- tránh feature suy đoán, abstraction chỉ dùng một lần và configurability không được yêu cầu;
- giữ diff surgical: không refactor, rename, reformat hoặc cleanup ngoài scope;
- chỉ thêm defensive handling cho trạng thái thực sự có thể xảy ra theo established contract;
- mọi dòng thay đổi phải truy được về request, acceptance evidence, regression/compatibility/security work bắt buộc, hoặc cleanup do patch tạo ra;
- biểu diễn step không-trivial theo dạng **step -> verification evidence** và chỉ retry khi có evidence mới hoặc thay đổi cụ thể.

## Comment & Documentation Policy

Trong build/review:
- ưu tiên name/structure để code tự giải thích;
- comment **WHY**, invariant, constraint và tradeoff không hiển nhiên thay vì kể lại WHAT;
- document public/shared contract khi hữu ích;
- TODO/FIXME phải actionable;
- update/xóa comment/docstring/docs stale trong vùng sửa;
- không thêm comment noise chỉ để tăng mật độ comment.

## Security-sensitive task

Kit không hứa "code an toàn tuyệt đối". Thay vào đó, workflow bắt buộc: security-sensitive changes không được silent pass nếu chưa có explicit security review/evidence.

Tự phân loại security-sensitive khi request/impact/diff chạm auth/authz, session/token/password, upload/filesystem, DB query với dữ liệu user kiểm soát, URL do user kiểm soát, HTML/template rendering, command execution, payment/webhook, secrets/credentials hoặc trust boundary tương đương.

Ví dụ — refresh token:

```text
rotation / expiry
revocation
replay risk
cookie flags
session fixation
authorization boundary
secret/token logging
```

Ví dụ — file upload:

```text
file size
extension/MIME
path traversal
filename sanitization
overwrite behavior
execution risk
storage boundary
authorization
```

Với các task này, lưu `security` state trong manifest v2 và bắt buộc current-head security diff review + targeted tests/checks + scanner/dependency-audit evidence khi có/phù hợp. Thiếu tooling phải ghi limitation explicit, không được silent pass.

## 25. Verify only

```text
@GitHub làm việc với PR #<number> trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Chỉ chạy verify + github-review.
Đối chiếu acceptance criteria với final diff và current-head CI.
```

Status:

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

---

## 26. Review PR

```text
@GitHub review PR #42 trong repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit/skills/github-review/SKILL.md.

Kiểm tra:
- đúng một schema-v2 manifest valid;
- manifest head khớp PR head;
- context nằm trong hard budget;
- scope/compatibility;
- missing consumers;
- tests;
- unresolved review threads;
- current-head CI.
```

---

## 27. Tiếp tục ở session mới

```text
@GitHub tiếp tục PR #42 trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore context từ schema-v2 task manifest trước khi tiếp tục.
```

Không cần chat transcript cũ.

---

## 28. Không nhớ PR number

Yêu cầu ChatGPT tìm open vibe PR theo:

- task ID;
- branch;
- title;
- request.

Nếu còn nhiều candidate, liệt kê thay vì đoán.

---

## 29. `CONTEXT_HIT`

Dùng khi manifest v2 duy nhất valid, budget-compliant và observed blob SHA không đổi.

Chỉ fetch current file cần cho bước tiếp theo.

---

## 30. `CONTEXT_REFRESH`

Dùng khi chỉ bounded minority observed files thay đổi.

Refresh file đổi và direct relationship cần thiết, sau đó update blob SHA/symbol/depth.

---

## 31. `CONTEXT_REBUILD`

Dùng khi:

- manifest thiếu/trùng/invalid/v1;
- scope đổi lớn;
- rebase/base làm invalid neighborhood;
- quá nhiều observed file đổi;
- context vượt hard limit;
- target cũ không còn phù hợp.

Rebuild vẫn bounded, không có nghĩa đọc cả repo.

---

## 32. Rebase/base đổi

Re-evaluate target/dependency/consumer. Nếu baseline đổi đáng kể thì `CONTEXT_REBUILD`.

---

## 33. CI fail

Flow:

```text
failed run
-> failed job
-> failed step/log
-> root cause
-> scoped fix
-> new head
-> old PASS/CI stale
-> verify new head
```

Không rerun mù khi failure có nguyên nhân deterministic rõ ràng.

---

## 34. Repo chưa có meaningful checks

Dùng:

```text
NEEDS_VERIFICATION_CONFIG
```

Không thêm no-op để tạo pass. Thiết lập test/lint/typecheck/build/smoke phù hợp nếu scope cho phép.

---

## 35. Verification head binding

Manifest:

```json
{
  "head_sha": "abc123",
  "verification": {
    "head_sha": "abc123",
    "ci_run_id": 123456,
    "status": "PASS_VERIFIED"
  }
}
```

PASS chỉ hợp lệ khi cả hai SHA cũng khớp actual current PR head.

Có commit mới thì PASS cũ stale.

---

## 36. Acceptance evidence

Mỗi criterion dùng structured evidence:

```json
{
  "id": "AC1",
  "expected": "Refresh succeeds after access expiry.",
  "status": "met",
  "evidence": [
    {
      "type": "test",
      "ref": "tests/test_auth.py::test_refresh_after_expiry"
    },
    {
      "type": "ci",
      "ref": "run:123456"
    }
  ]
}
```

Không mark `met` chỉ dựa prose không có evidence.

---

## 37. Migrate PR schema v1

Schema v1 không còn là normal continuation state.

Với old active PR:

1. đọc current base/head/diff;
2. rebuild bounded neighborhood;
3. thêm `context.symbols`;
4. thêm `role`, `depth`, `symbols` cho observed files;
5. đổi acceptance evidence thành list có cấu trúc;
6. thêm `verification.head_sha`;
7. replace block cũ bằng đúng một v2 block;
8. verify current head trước khi PASS.

---

## 38. Nhiều task song song

Mỗi task một branch + PR:

```text
PR #41 feature
PR #42 bug fix
PR #43 docs
```

Không có shared `current-task.json`.

---

## 39. Merge

Kit không merge mặc định.

```text
@GitHub kiểm tra PR #42.
Nếu current head PASS_VERIFIED và không có blocker,
squash merge vào main.
```

Chỉ merge khi user hoặc repository instructions authorize rõ ràng.

---

# Prompt mẫu

## Full implementation

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit và chạy full vibe workflow.

Task:
<mô tả>

Yêu cầu:
- ...
- ...

Respect hard context budget.
Không mở rộng scope.
Chỉ coi hoàn tất khi current-head verification pass.
```

## Fix bug

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>

Bắt buộc:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
Dùng iterative symbol-aware search và giữ context bounded.
```

## Refactor

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Refactor:
<target>

Giữ behavior/public contract.
Tìm direct dependencies và consumers.
Capture baseline.
Search old references sau sửa.
Verify current head.
```

## Test-only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Mode: test

Thêm tests cho:
<module/feature>

Cover:
<cases>

Không đổi production behavior nếu không được yêu cầu.
```

## Docs-only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Mode: docs

Cập nhật:
<README/docs>

Chỉ dùng code/config context cần thiết để verify claim trong tài liệu.
```

## Continue

```text
@GitHub tiếp tục PR #<number> trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore strict v2 manifest, check budget/blob SHA rồi tiếp tục.
```

## Plan only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

CHỈ PLAN. Không sửa code.

Task:
<mô tả>
```

## Verify only

```text
@GitHub làm việc với PR #<number> trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Chỉ verify + github-review.
Yêu cầu verification.head_sha khớp current PR head.
```

---

# Chọn mode

| Công việc | Mode |
| --- | --- |
| Project/chức năng mới | `feature` |
| Thay đổi behavior/compatibility | `change` |
| Sửa defect | `bug_fix` |
| Tái cấu trúc giữ behavior | `refactor` |
| Production fix tối thiểu khẩn cấp | `hotfix` |
| Test/coverage-only | `test` |
| README/docs/examples/metadata | `docs` |

---

# Nguyên tắc cốt lõi

1. Một task thực tế thường dùng một PR.
2. Continue từ GitHub state, không từ pasted chat history.
3. PR phải có đúng một strict schema-v2 manifest.
4. Persist references/symbols/blob SHA, không persist source copy.
5. Respect hard context limits.
6. Dùng iterative symbol-aware retrieval thay filename-only search.
7. Static dependency chỉ advisory.
8. Bug phải có evidence-supported root cause.
9. Refactor phải discover consumers và capture baseline.
10. `PASS_VERIFIED` phải thuộc current head SHA.
11. Commit mới làm PASS cũ stale.
12. Không có meaningful checks thì dùng `NEEDS_VERIFICATION_CONFIG`, không fake pass.
13. Comment dùng cho rationale không hiển nhiên; không kể lại code obvious và phải giữ docs/comment trong vùng sửa luôn current.
14. Security-sensitive change bắt buộc explicit current-head security evidence; không coi PASS thông thường là security guarantee.
