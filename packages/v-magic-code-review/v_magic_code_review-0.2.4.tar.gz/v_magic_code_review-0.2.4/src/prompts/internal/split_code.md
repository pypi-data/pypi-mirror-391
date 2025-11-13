# **任务：**

由于大型 Code Diff 直接进行 Code Review 可能会导致结果不准确，我需要你将这份 Code Diff 拆分成多个逻辑相关的、更小的审查单元。

# **输出格式：**

你必须严格按照以下 JSON 格式输出：

```json
[
    {
        "summary": "变更摘要（例如：用户界面与相关 API 更新）",
        "lines": 700,
        "files": [
            "src/components/UserProfile.js",
            "src/styles/UserProfile.css",
            "src/controllers/UserController.js"
        ]
    },
    {
        "summary": "变更摘要（例如：数据库模型更新）",
        "lines": 325,
        "files": [
            "src/models/UserModel.js",
            "src/migrations/20240601_add_user_fields.js"
        ]
    }
]
```

# **拆分规则和约束：**

1. **逻辑分组（Summary）：** 根据功能的关联性（例如：功能模块、API、UI 页面、数据库模型等）创建审查组，并为每个组提供一个简短的 `summary`。
2. **行数统计（Lines）：** `lines` 字段必须准确计算该组 `files` 列表中所有文件的**变更行数总和**（增加或修改的行）。
3. **行数限制：** 每个审查组（`summary`）的 `lines` 总数**必须在 500 到 1000 行之间**。

# **Code Diff：**

{mr_diff}