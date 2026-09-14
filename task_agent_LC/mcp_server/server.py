import json
from pathlib import Path
from mcp.server import FastMCP

TASK_FILE=Path(__file__).parent.parent/"storage"/"tasks.json"
mcp=FastMCP("Task Manager")

def load_tasks():
    if not TASK_FILE.exists():
        return []
    with open(TASK_FILE,"r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASK_FILE,"w") as f:
        json.dump(tasks,f,indent=2)

@mcp.tool()
def add_task(task:str)->str:
    tasks=load_tasks()
    tasks.append({"task":task,"completed":False})
    save_tasks(tasks)
    return f"Task added successfully: {task}"

@mcp.tool()
def list_tasks()->str:
    tasks=load_tasks()
    if not tasks:
        return "There are no tasks."
    result=[]
    for i,task in enumerate(tasks):
        status="completed" if task["completed"] else "pending"
        result.append(f"{i}: {task['task']} [{status}]")
    return "\n".join(result)

@mcp.tool()
def complete_task(task_id:int)->str:
    tasks=load_tasks()
    if task_id<0 or task_id>=len(tasks):
        return "Invalid task ID."
    tasks[task_id]["completed"]=True
    save_tasks(tasks)
    return f"Task completed: {tasks[task_id]['task']}"

if __name__=="__main__":
    mcp.run(transport="stdio")