# Thư viện prompt

Copy template ngắn nhất phù hợp với task.

## Full implementation

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

## Sửa bug

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Fix:
<triệu chứng>

Bắt buộc:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

## Refactor

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Refactor <target>.
Giữ nguyên behavior/public contract.
Tìm direct dependency và consumer, chụp baseline, search reference cũ sau khi sửa và verify current head.
```

## Chỉ viết test

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Mode: test
Thêm test cho <module/behavior>.
Không thay đổi production behavior nếu chưa được yêu cầu.
```

## Chỉ sửa docs

```text
@GitHub làm việc với repo <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.

Mode: docs
Cập nhật <README/docs/examples>.
Chỉ đọc source/config cần thiết để kiểm chứng nội dung.
```

## Tiếp tục task

```text
@GitHub tiếp tục PR #<number> trong <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Restore schema-v2 manifest và GitHub state hiện tại rồi tiếp tục.
```

## Review

```text
@GitHub review PR #<number> trong <owner>/<repo>.
Sử dụng cuongtobi/gpt-web-vibe-kit.
Kiểm tra scope, current-head verification, acceptance evidence và blocker còn lại.
```

## Merge

```text
@GitHub kiểm tra PR #<number>.
Nếu current head đã ready và không còn blocker, squash merge vào main.
```
