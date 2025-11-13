**任务：**

由于大型 Code Diff 直接进行 Code Review 可能会导致结果不准确，我需要你将这份 Code Diff 拆分成多个逻辑相关的、更小的审查单元。

**输出格式：**

你必须严格按照以下 JSON 格式输出：

```json
{
    "frontend": [
        {
            "summary": "变更摘要（例如：用户界面更新）",
            "lines": 350,
            "files": [
                "src/components/UserProfile.js",
                "src/styles/UserProfile.css"
            ]
        }
    ],
    "backend": [
        {
            "summary": "变更摘要（例如：数据库模型更新）",
            "lines": 325,
            "files": [
                "src/models/UserModel.js",
                "src/migrations/20240601_add_user_fields.js"
            ]
        }
    ]
}
```

**拆分规则和约束：**

1. **顶级分类：** 必须分为 `frontend` 和 `backend` 两个根键。
2. **逻辑分组（Summary）：** 在 `frontend` 和 `backend` 内部，根据代码的关联性（例如：功能模块、API、UI 页面、数据库模型等）创建审查组，并为每个组提供一个简短的 `summary`。
3. **行数统计（Lines）：** `lines` 字段必须准确计算该组 `files` 列表中所有文件的**变更行数总和**（增加或修改的行）。
4. **行数限制：** 每个审查组（`summary`）的 `lines` 总数**不应超过 500 行**。
5. **例外情况：** 如果一个**单独的文件**本身就超过 500 行，则它自己单独成为一组，此时 `lines` 可以超过 500。

**Code Diff：**

{mr_diff}