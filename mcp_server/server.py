import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer

TASK_FILE=Path(__file__).parent.parent/"storage"/"tasks.json"
server=MCPServer("Task Manager")

def load_tasks():
    if not TASK_FILE.exists():
        return []
    with open(TASK_FILE,"r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASK_FILE,"w") as f:
        json.dump(tasks,f,indent=2)

@server.tool()
async def add_task(task: str)->str:
    """Add a new task."""
    tasks=load_tasks()
    tasks.append({
        "task":task,
        "completed":False
    })
    save_tasks(tasks)
    return f"Task added successfully: {task}"

@server.tool()
async def list_tasks()->str:
    """Return all tasks."""
    tasks=load_tasks()
    if not tasks:
        return "There are no tasks."
    result=[]
    for i,task in enumerate(tasks):
        status="completed" if task["completed"] else "pending"
        result.append(f"{i}: {task['task']} [{status}]")
    return "\n".join(result)

@server.tool()
async def complete_task(task_id:int)->str:
    """Mark a task as completed."""
    tasks=load_tasks()
    if task_id<0 or task_id>=len(tasks):
        return "Invalid task ID."
    tasks[task_id]["completed"]=True
    save_tasks(tasks)
    return f"Task completed: {tasks[task_id]['task']}"

if __name__=="__main__":
    server.run()
