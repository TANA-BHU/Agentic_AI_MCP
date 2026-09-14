TEST_CASES=[
    {
        "name":"Add task",
        "input":"Add a task to study transformers",
        "expected_keywords":["added"]
    },
    {
        "name":"List tasks",
        "input":"Show me my tasks",
        "expected_keywords":["transformers"]
    },
    {
        "name":"Invalid task",
        "input":"Complete task 999",
        "expected_keywords":["invalid"]
    }
]