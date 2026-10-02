# gpt-web-vibe-kit

[English](README.md) · [Hướng dẫn sử dụng](docs/usage-vi.md) · [Thư viện prompt](docs/prompts/common-vi.md) · [Task reference](docs/reference/task-manifest.md)

Workflow coding GitHub-native cho **ChatGPT Web + GitHub**, tối ưu cho repository cá nhân nhỏ và vừa.

```text
session -> plan -> build -> verify -> github-review
```

Ý tưởng chính: **GitHub là durable state; không cần phụ thuộc chat cũ.**

## Bắt đầu nhanh

### 1. Bootstrap repository

```text
@GitHub làm việc với repo <owner>/<repo>.

Sử dụng cuongtobi/gpt-web-vibe-kit.
Đọc skills/bootstrap/SKILL.md và bootstrap repository này.

Giữ nguyên AGENTS.md nếu đã tồn tại.
Detect stack, entrypoint và verification command hiện có.
```

### 2. Bắt đầu task

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit và chạy full vibe workflow.

Task:
<mô tả>

Yêu cầu:
- giữ <contract>;
- có focused tests;
- không thêm dependency nếu không cần.
```

### 3. Tiếp tục ở session ChatGPT khác

```text
@GitHub tiếp tục PR #<number> trong <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore context từ schema-v2 PR manifest rồi tiếp tục.
```

Không cần paste lại chat cũ.

## Chọn workflow

- [Bắt đầu task mới](docs/workflows/new-task.md)
- [Tiếp tục task đang làm](docs/workflows/continue-task.md)
- [Sửa bug](docs/workflows/bug-fix.md)
- [Thêm/thay đổi tính năng](docs/workflows/feature-change.md)
- [Refactor](docs/workflows/refactor.md)
- [Chỉ viết test](docs/workflows/test-only.md)
- [Chỉ sửa docs](docs/workflows/docs-only.md)
- [Frontend/UI](docs/workflows/frontend.md)

CI failure, review, rebase, merge và nhiều task song song nằm trong [task operations](docs/usage-vi.md#task-operations).

## Cách hoạt động

Mỗi task dùng một branch và một pull request. PR body lưu đúng một task manifest schema v2 chứa các reference có giới hạn tới target, symbol, dependency, consumer, test, acceptance criteria và verification evidence của current head.

Source luôn lấy từ GitHub hiện tại thay vì copy vào task state. Context bị giới hạn bởi `.vibe/config.json`; PR head thay đổi thì verification cũ trở thành stale.

## Frontend state tùy chọn

Task UI có thể thêm block `frontend` để lưu intent refine/redesign, acceptance mapping và visual-QA evidence có giới hạn. Task không chạm UI thì bỏ qua block này.

Xem [Frontend workflow](docs/workflows/frontend.md).

## Security

Task security-sensitive vẫn chạy workflow bình thường nhưng không được pass âm thầm nếu thiếu security evidence của current head. Kit không tuyên bố code được đảm bảo an toàn tuyệt đối.

Xem [Security reference](docs/reference/security.md).

## Bản đồ tài liệu

- [Usage](docs/usage-vi.md) — chọn việc bạn muốn làm.
- [Prompt library](docs/prompts/common-vi.md) — prompt copy/paste.
- [Task manifest](docs/reference/task-manifest.md) — task state trong PR.
- [Context](docs/reference/context.md) — bounded retrieval và restore.
- [Verification](docs/reference/verification.md) — current-head evidence và completion.
- [Security](docs/reference/security.md) — classification và evidence.
- [Configuration](docs/reference/configuration.md) — `.vibe/config.json`.

## Check khi phát triển chính repository này

```bash
python -m pip install "jsonschema>=4,<5"
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/retrieval.py runtime/vibe_web.py
```

Runtime vẫn chỉ dùng Python standard library.
