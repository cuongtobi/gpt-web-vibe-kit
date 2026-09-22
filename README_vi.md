# gpt-web-vibe-kit

Bộ vibe-coding GitHub-native cho **ChatGPT Web + GitHub**, lấy tư tưởng từ [my-vibe-kit](https://github.com/cuongtobi/my-vibe-kit) nhưng thiết kế lại cho session Web không có local checkout bền vững.

```text
session -> plan -> build -> verify -> github-review
```

## Ý tưởng cốt lõi
Session mới không đọc lại toàn bộ repo và không cần chat cũ. Context được dựng lại từ:

```text
AGENTS.md
+ .vibe/project-context.json
+ task manifest trong PR
+ PR diff hiện tại
+ source liên quan hiện tại
+ CI của current head
= working context
```

Task manifest lưu **cần đọc cái gì**, không lưu bản sao toàn bộ source.

## State
Project state ổn định:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
```

State của từng task nằm trong PR body. Không dùng `current-task.json` chung trên `main`, nên nhiều task/PR có thể chạy song song.

## Session mới
Skill `session`:

1. Đọc `AGENTS.md`, `.vibe/config.json`, `.vibe/project-context.json`.
2. Xác định task từ PR/branch/task user chỉ định hoặc vibe PR phù hợp đang mở.
3. Parse task manifest từ PR body.
4. So sánh blob SHA đã lưu với file hiện tại.
5. Chọn `CONTEXT_HIT`, `CONTEXT_REFRESH` hoặc `CONTEXT_REBUILD`.
6. Chỉ fetch target + dependency + consumer + test có giới hạn.
7. Đọc current diff và CI mới nhất.

## Fix bug
```text
symptom -> symbol/file -> target -> dependency -> consumer -> test
        -> reproduce -> root cause -> regression test -> minimal fix
```

## Refactor
```text
target -> dependency -> toàn bộ direct consumer tìm được
       -> test/contract -> baseline -> refactor -> verify behavior
```

Refactor phải chú trọng reverse dependency/consumer.

## Skills
```text
skills/
├── bootstrap/SKILL.md
├── session/SKILL.md
├── vibe/SKILL.md
├── plan/SKILL.md
├── build/SKILL.md
├── verify/SKILL.md
└── github-review/SKILL.md
```

## Bootstrap project local
```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

Installer tạo `.vibe/config.json`, `.vibe/project-context.json`, `.vibe/README.md`; chỉ tạo `AGENTS.md` khi target chưa có.

Trên ChatGPT Web, skill `bootstrap` tạo contract tương tự trực tiếp bằng GitHub.

## Cách dùng
```text
@GitHub làm việc với cuongtobi/sample-api.
Đọc cuongtobi/gpt-web-vibe-kit/skills/vibe/SKILL.md và chạy workflow.
Fix refresh-token rotation sau khi session hết hạn.
```

Session khác:
```text
@GitHub tiếp tục PR #42 trong cuongtobi/sample-api bằng gpt-web-vibe-kit.
```

## Dependency
Kit đọc import/framework registration quanh target, search usage/import để tìm consumer, dùng adapter làm search hint, rồi lưu path/symbol/blob SHA vào PR task manifest.

Dependency luôn là `static-best-effort / advisory`. Dynamic import, DI, generated route/code, macro, reflection, Rails/WordPress runtime wiring, bundler alias và registry cần native tool, test, CI hoặc kiểm tra trực tiếp.

## Verification
- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

Chỉ `PASS_VERIFIED` khi evidence thuộc current PR head SHA. CI xanh của head cũ là stale evidence.
