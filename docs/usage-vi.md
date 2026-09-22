# Hướng dẫn sử dụng gpt-web-vibe-kit

Tài liệu này mô tả cách dùng `gpt-web-vibe-kit` trên **ChatGPT Web + GitHub** cho các tình huống coding phổ biến.

Workflow chuẩn:

```text
session -> plan -> build -> verify -> github-review
```

Kit không phụ thuộc vào chat history. Mỗi task dùng GitHub repository + branch + pull request + task manifest + CI làm nguồn trạng thái bền vững.

---

## 1. Chuẩn bị một repository để dùng kit

### Repository đã có code

Prompt:

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit.
Đọc skills/bootstrap/SKILL.md và bootstrap repo này để dùng workflow của kit.

Không overwrite AGENTS.md nếu repo đã có.
Phân tích stack, framework, entrypoint và các command test/lint/typecheck/build hiện có.
```

ChatGPT phải:

1. đọc repo hiện tại;
2. giữ nguyên `AGENTS.md` nếu đã tồn tại;
3. tạo `.vibe/config.json`, `.vibe/project-context.json`, `.vibe/README.md`;
4. ghi lại languages, primary language, frameworks, entrypoints, verification commands và context limits;
5. commit thay đổi qua branch/PR phù hợp.

### Repository trống

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit để bootstrap repo mới.

Project:
<mô tả project>

Tech stack:
<stack nếu đã biết>
```

Project contract được tạo trước, sau đó task build project chạy theo workflow `vibe`.

---

## 2. Build dự án mới từ đầu

Ví dụ:

```text
@GitHub làm việc với repo cuongtobi/sample-fastapi.

Sử dụng cuongtobi/gpt-web-vibe-kit.

Build một REST API quản lý task bằng FastAPI + PostgreSQL.

Yêu cầu:
- CRUD task;
- validation bằng Pydantic;
- SQLAlchemy;
- migration;
- pytest;
- Ruff;
- cấu trúc dễ mở rộng;
- README chạy local.

Chạy toàn bộ workflow vibe.
```

Flow:

```text
new project request
      ↓
bootstrap project context
      ↓
plan architecture
      ↓
create task branch + PR
      ↓
build initial structure
      ↓
tests/config/docs
      ↓
CI
      ↓
verify
      ↓
ready
```

Plan phải xác định:

- stack;
- framework-native structure;
- entrypoints;
- package/dependency setup;
- database/config boundaries;
- test strategy;
- acceptance criteria;
- CI commands.

Với project mới, context ban đầu đến từ:

```text
user requirements
+ chosen stack
+ generated project structure
+ config/manifests
```

Sau khi code được tạo, PR manifest bắt đầu lưu target, test và dependency reference quan trọng để session sau tiếp tục.

---

## 3. Thêm chức năng mới

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit.

Thêm chức năng export báo cáo ra CSV.

Yêu cầu:
- giữ nguyên API hiện tại;
- export các field đang hiển thị trong report;
- có test;
- không thêm dependency mới nếu không cần.

Chạy workflow vibe đầy đủ.
```

Flow:

```text
feature request
   ↓
restore project/session context
   ↓
search entrypoint liên quan
   ↓
find target modules
   ↓
dependencies
   ↓
consumers/contracts
   ↓
tests
   ↓
plan
   ↓
build
   ↓
verify
```

ChatGPT nên tìm bằng route, component, class, function, error/string và import usage, không chỉ dựa vào filename.

---

## 4. Thay đổi behavior hiện có

Mode: `change`.

Ví dụ:

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Thay trailing stop từ fixed points sang hỗ trợ cả fixed points và percentage.

Yêu cầu:
- config cũ vẫn hoạt động;
- percentage là optional;
- không phá persisted config cũ;
- có compatibility test.
```

Plan phải phân biệt:

```text
current behavior
→ desired behavior
→ compatibility contract
→ affected consumers
→ tests
```

Đặc biệt kiểm tra public API, config format, database/schema, serialized data và backward compatibility.

---

## 5. Fix bug

Prompt nên mô tả symptom càng cụ thể càng tốt.

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Fix bug:
Refresh token thất bại khi access token đã hết hạn nhưng refresh token vẫn còn hợp lệ.

Tái hiện bug trước.
Tìm root cause.
Thêm regression test.
Chỉ sửa root cause, không refactor ngoài scope.
Chạy verification đầy đủ.
```

Flow bắt buộc:

```text
REPRODUCE
   ↓
ROOT CAUSE
   ↓
FAILING REGRESSION TEST
   ↓
MINIMAL FIX
   ↓
PASSING REGRESSION TEST
   ↓
AFFECTED TESTS
   ↓
VERIFY
```

Context retrieval có thể bắt đầu bằng:

```text
refresh
token
session
expired
```

Sau đó mở rộng:

```text
dependencies
     ↓
   target
     ↑
consumers
     +
   tests
```

Nếu root cause chưa được chứng minh, không sửa code dựa trên đoán.

Prompt ngắn:

```text
@GitHub repo <owner>/<repo>
Use gpt-web-vibe-kit.
Fix <bug>.
Reproduce -> root cause -> regression test -> minimal fix -> verify.
```

---

## 6. Hotfix production

Mode: `hotfix`.

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

HOTFIX:
<symptom production>.

Yêu cầu:
- scope nhỏ nhất có thể;
- không rename;
- không cleanup;
- không upgrade package;
- không refactor ngoài lỗi;
- có regression test nếu khả thi;
- verify các path bị ảnh hưởng.
```

Hotfix ưu tiên diff nhỏ và tránh thay đổi kiến trúc.

---

## 7. Viết test cho code hiện có

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Viết test cho module payment.

Cover:
- happy path;
- invalid input;
- payment gateway timeout;
- duplicate payment.

Không thay đổi production behavior trừ khi phát hiện bug thật và tôi yêu cầu fix.
```

Flow:

```text
target module
   ↓
public behavior
   ↓
dependencies/external boundaries
   ↓
current tests
   ↓
missing cases
   ↓
add tests
   ↓
run verification
```

Nếu test mới phát hiện bug ngoài scope, ghi rõ bug thay vì âm thầm sửa production code.

---

## 8. Tăng test coverage

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Tăng test coverage cho package auth.

Ưu tiên:
1. business-critical behavior;
2. error paths;
3. security edge cases;
4. regression-prone code.

Không viết test chỉ để tăng phần trăm coverage.
```

Ưu tiên giá trị behavior thay vì mục tiêu coverage tuyệt đối.

---

## 9. Refactor function/class/module

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Refactor AuthService:
- tách token logic thành TokenService;
- tách session logic thành SessionService;
- giữ nguyên public API hiện tại;
- không đổi behavior.

Trước khi sửa:
- tìm toàn bộ direct consumers;
- chạy baseline tests;
- ghi invariants.

Sau khi sửa:
- search lại references cũ;
- chạy affected tests và CI.
```

Flow:

```text
target
  ↓
dependencies
  ↓
ALL discoverable consumers
  ↓
tests/contracts
  ↓
baseline
  ↓
refactor
  ↓
search old references
  ↓
verify unchanged behavior
```

Acceptance criteria nên mô tả invariants như response, public method signature, DB schema hoặc behavior phải giữ nguyên.

---

## 10. Refactor lớn nhiều module

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Refactor module billing sang feature-first architecture.

Không đổi behavior.

Trước implementation:
- lập dependency/consumer map;
- xác định public boundaries;
- chia migration thành các bước nhỏ;
- xác định test baseline.

Nếu scope quá lớn cho một PR, chia thành nhiều PR độc lập có thứ tự.
```

Ví dụ:

```text
PR1: introduce boundary
PR2: migrate consumers
PR3: remove old implementation
```

---

## 11. Rename file/class/API

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Rename UserManager thành UserService.

Yêu cầu:
- tìm tất cả imports/usages;
- cập nhật tests;
- kiểm tra string reference/config/DI/serialization nếu có;
- không để lại old references.
```

Đây là dạng `refactor`.

---

## 12. Thêm API endpoint

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Thêm endpoint:
POST /api/v1/reports/export

Yêu cầu:
- auth giống endpoint report hiện tại;
- validate input;
- dùng report service hiện có;
- trả file CSV;
- có API tests;
- cập nhật OpenAPI nếu framework không tự làm.
```

Context thường là:

```text
route/controller
↓
request/response schema
↓
service/use-case
↓
repository/data boundary
↓
auth/middleware
↓
tests
```

---

## 13. Thêm database field / migration

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Thêm field timezone vào User.

Yêu cầu:
- default UTC cho user cũ;
- migration an toàn;
- API cũ không bị break;
- update schema/model/serializer;
- có migration hoặc integration test phù hợp.
```

Plan phải kiểm tra model, migration, serializer/DTO, API contract, query, existing data và tests.

---

## 14. Thêm package mới

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Tôi muốn dùng <package> để <goal>.

Trước khi thêm:
- kiểm tra project hiện tại có khả năng tương đương không;
- giải thích vì sao cần dependency mới;
- kiểm tra compatibility;
- update lockfile;
- thêm verification phù hợp.
```

Kit không nên thêm package chỉ vì implementation thuận tiện hơn.

---

## 15. Upgrade dependency/framework

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Upgrade <framework> từ <old> lên <new>.

Phân tích breaking changes có liên quan đến code trong repo.
Lập impact map.
Chia migration thành bước nhỏ nếu cần.
Chạy full affected tests/build.
```

Mode thường là `change`.

---

## 16. Frontend feature

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Thêm filter theo status vào trang Orders.

Yêu cầu:
- giữ query params khi reload;
- không fetch dữ liệu dư thừa;
- mobile vẫn hoạt động;
- thêm component/integration test phù hợp.
```

Context:

```text
route/page
↓
feature UI
↓
hook/composable/store
↓
API/data layer
↓
tests
```

Với Next.js, Nuxt và SvelteKit phải kiểm tra server/client boundaries.

---

## 17. Frontend bug

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Fix bug:
Sau khi edit profile, UI hiển thị dữ liệu cũ cho đến khi refresh browser.

Tìm root cause trước.
Kiểm tra state/cache/query invalidation.
Thêm regression test nếu test harness hỗ trợ.
```

Root cause có thể nằm ở query cache, store, API mutation, stale props hoặc server/client data boundary.

---

## 18. WordPress plugin/theme

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Repo này là WordPress theme/plugin.
Thêm <feature>.

Không sửa WordPress core.
Kiểm tra:
- hooks/filters;
- REST routes;
- options/meta;
- template/block contracts;
- enqueue assets;
- compatibility với behavior hiện tại.
```

WordPress hook graph chỉ là best-effort, không phải absolute truth.

---

## 19. Rails/Laravel/Django/Nest và framework magic

Có thể bổ sung trong prompt:

```text
Khi phân tích dependency, không chỉ dựa trên static imports.
Kiểm tra framework registration/DI/routes/callbacks và dùng native tests/tooling để verify.
```

Kit đã có adapter hints cho các framework chính.

---

## 20. Chỉ phân tích / chỉ lập plan

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Chỉ PLAN, không sửa code.

Phân tích việc chuyển authentication từ session cookie sang JWT.

Tôi cần:
- current architecture;
- affected modules;
- dependency/consumer impact;
- migration risks;
- compatibility;
- test plan;
- đề xuất chia PR.
```

Workflow dừng ở:

```text
session -> plan
```

---

## 21. Review code / PR

```text
@GitHub review PR #42 trong repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit/skills/github-review/SKILL.md.

Kiểm tra:
- scope so với task manifest;
- bugs/regressions;
- missing consumers;
- compatibility;
- tests;
- current-head CI;
- unresolved review threads.
```

Nếu PR head thay đổi sau review thì evidence review cũ phải được coi là stale cho phần code thay đổi.

---

## 22. Verify task đã code xong

```text
@GitHub làm việc với PR #42 của repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Chỉ chạy phase verify + github-review.
Không thêm feature mới.

Đối chiếu acceptance criteria với current-head CI và final diff.
```

Output:

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

---

## 23. Tiếp tục task ở session mới

Prompt khuyên dùng:

```text
@GitHub tiếp tục PR #42 trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Đọc task manifest trong PR và restore context trước.
Tiếp tục từ trạng thái hiện tại.
```

Flow:

```text
read project context
↓
read PR manifest
↓
read head SHA
↓
compare observed blob SHAs
↓
CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
↓
fetch bounded code
↓
continue
```

Không cần paste lại chat cũ.

---

## 24. Không nhớ PR number

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng gpt-web-vibe-kit.

Tôi muốn tiếp tục task "refresh token".
Tìm vibe PR đang mở phù hợp và restore context.
```

Match bằng PR title, branch, task manifest request và task_id. Nếu còn nhiều candidate thì phải liệt kê thay vì chọn ngẫu nhiên.

---

## 25. Code bị người khác sửa giữa hai session

Session mới so:

```text
stored blob SHA
vs
current blob SHA
```

- `CONTEXT_HIT`: relevant references không đổi.
- `CONTEXT_REFRESH`: refresh subset thay đổi + neighborhood.
- `CONTEXT_REBUILD`: scope/baseline thay đổi lớn hoặc quá nhiều observed files thay đổi.

---

## 26. Branch vừa rebase main

```text
@GitHub tiếp tục PR #42.
PR vừa rebase main.

Sử dụng gpt-web-vibe-kit.
Re-evaluate context và impact trước khi code tiếp.
```

Nếu rebase làm thay đổi nhiều target/dependency, chọn `CONTEXT_REBUILD`.

---

## 27. CI fail

```text
@GitHub tiếp tục PR #42.
Sử dụng gpt-web-vibe-kit.

CI đang fail.
Đọc failed jobs/steps/logs.
Xác định root cause.
Chỉ sửa lỗi thật.
Rerun verification cho current head.
```

Flow:

```text
failed CI
↓
job
↓
step
↓
log
↓
root cause
↓
fix
↓
new head
↓
old CI stale
↓
verify new head
```

---

## 28. Repo chưa có tests/checks

Nếu không có meaningful verification:

```text
NEEDS_VERIFICATION_CONFIG
```

Prompt:

```text
Repo chưa có meaningful verification.
Hãy thiết lập verification tối thiểu hợp lý cho stack này trước khi coi task hoàn tất.
Không dùng no-op command để tạo PASS.
```

Có thể dùng test, lint, typecheck, build hoặc smoke test tùy stack.

---

## 29. Merge PR

Kit không tự merge mặc định.

```text
@GitHub kiểm tra PR #42.
Nếu current head PASS_VERIFIED và không còn blocker, squash merge vào main.
```

Flow:

```text
verify current head
↓
review final diff
↓
check CI
↓
check blocker
↓
merge
↓
post-merge CI nếu có
```

---

## 30. Nhiều task song song

Mỗi task dùng branch + PR riêng:

```text
PR #41 = feature export CSV
PR #42 = bug refresh token
PR #43 = refactor billing
```

Không có shared `current-task.json`, nên state không đè nhau.

---

# Prompt chuẩn khuyên dùng

## Full implementation

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit và chạy workflow vibe đầy đủ.

Task:
<mô tả>

Yêu cầu:
- <requirement 1>
- <requirement 2>

Không mở rộng scope ngoài yêu cầu.
Chỉ coi hoàn tất khi current-head verification pass.
```

## Fix bug

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Fix bug:
<symptom>

Bắt buộc:
reproduce -> root cause -> regression test -> minimal fix -> affected tests -> verify.
```

## Refactor

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Refactor:
<target>

Giữ nguyên behavior/public contract.
Tìm dependencies + tất cả direct consumers.
Capture baseline trước khi sửa.
Search old references sau khi sửa.
Verify current head.
```

## Test-only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Viết test cho:
<module/feature>

Cover:
<cases>

Không thay production behavior trừ khi tôi yêu cầu.
```

## Continue session

```text
@GitHub tiếp tục PR #<number> trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore context từ PR manifest rồi tiếp tục task.
```

## Plan only

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Chỉ PLAN, không sửa code.

Task:
<mô tả>
```

## Verify only

```text
@GitHub làm việc với PR #<number> trong repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Chỉ verify + github-review.
Đối chiếu acceptance criteria với current-head diff và CI.
```

---

# Chọn mode

| Công việc | Mode |
| --- | --- |
| Tạo project/chức năng mới | `feature` |
| Thay đổi behavior hiện có | `change` |
| Sửa lỗi | `bug_fix` |
| Tái cấu trúc không đổi behavior | `refactor` |
| Sửa production khẩn cấp | `hotfix` |
| Chỉ thêm test | test-only task, thường không đổi production behavior |

---

# 10 nguyên tắc quan trọng

1. Mỗi task thực tế nên có một PR riêng.
2. Session mới tiếp tục bằng PR, không bằng cách paste lại chat cũ.
3. Task manifest lưu reference, không lưu full source.
4. Current GitHub code luôn authoritative hơn manifest cũ.
5. Static dependency chỉ advisory.
6. Bug phải tìm root cause trước khi fix.
7. Refactor phải tìm consumers và baseline behavior.
8. PASS phải thuộc current head SHA.
9. Head thay đổi thì CI/review evidence cũ trở thành stale.
10. Không có meaningful checks thì dùng `NEEDS_VERIFICATION_CONFIG`, không fake PASS.
