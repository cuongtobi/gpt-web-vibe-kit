# Hướng dẫn sử dụng

Đây là trang bắt đầu khi dùng `gpt-web-vibe-kit` trên **ChatGPT Web + GitHub**.

```text
session -> plan -> build -> verify -> github-review
```

Chọn đúng việc bạn muốn làm; chi tiết contract được tách riêng sang phần reference.

## Bắt đầu ở đây

- Repository/task mới: [Bắt đầu task mới](workflows/new-task.md)
- Đã có PR hoặc chuyển sang session ChatGPT khác: [Tiếp tục task](workflows/continue-task.md)
- Muốn copy prompt ngay: [Thư viện prompt tiếng Việt](prompts/common-vi.md)

## Chọn workflow

| Mục tiêu | Hướng dẫn | Mode |
| --- | --- | --- |
| Tạo project/chức năng mới | [New task](workflows/new-task.md) | `feature` |
| Thay đổi behavior hiện có | [Feature/change](workflows/feature-change.md) | `change` |
| Sửa lỗi | [Bug fix](workflows/bug-fix.md) | `bug_fix` |
| Đổi cấu trúc nhưng giữ behavior | [Refactor](workflows/refactor.md) | `refactor` |
| Chỉ thêm regression/coverage tests | [Test-only](workflows/test-only.md) | `test` |
| Chỉ sửa README/docs/examples/metadata | [Docs-only](workflows/docs-only.md) | `docs` |
| Task chạm UI/frontend | [Frontend](workflows/frontend.md) | tùy task |

Hotfix production dùng mode `hotfix`, giữ scope nhỏ nhất và tuân theo kỷ luật bug-fix.

## Task operations

Đây là thao tác trong vòng đời task, không phải mode riêng:

- [CI failure](operations/ci-failure.md)
- [Review PR](operations/review.md)
- [Rebase/base branch thay đổi](operations/rebase.md)
- [Merge](operations/merge.md)
- [Nhiều task song song](operations/concurrent-tasks.md)

## Reference

Chỉ cần đọc khi muốn hiểu contract:

- [Task manifest](reference/task-manifest.md)
- [Context và restore](reference/context.md)
- [Verification và completion](reference/verification.md)
- [Security](reference/security.md)
- [Configuration](reference/configuration.md)

## Prompt library

- [Prompt tiếng Việt](prompts/common-vi.md)
- [Prompt English](prompts/common.md)

## Source of truth

Tài liệu cho người dùng nằm trong `docs/`. Hành vi agent nằm trong `skills/`. Machine contract nằm trong `schemas/` và `runtime/`. Instruction riêng của repository nằm trong `AGENTS.md`.

Cách chia này tránh copy policy dài qua nhiều file usage.
