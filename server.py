import os
import uuid
import uvicorn

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import UJSONResponse, StreamingResponse
from starlette.background import BackgroundTask

from utils import extract_audio, m4a_to_mp3, generate

tasks = {}

app = Starlette()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[os.environ["HOST"]])
app.add_middleware(CORSMiddleware, allow_origins=[os.environ["ORIGIN"]])


@app.route("/", methods=["GET"])
def home():
    return UJSONResponse({"msg": "api is running"})


@app.route("/download", methods=["POST"])
async def download(request):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "Pending"}

    json = await request.json()
    url = json.get("url")
    task = BackgroundTask(extract_audio, url, task_id=task_id, state=tasks)

    return UJSONResponse(
        {"status": app.url_path_for("status", task_id=task_id)}, background=task
    )


@app.route("/convert/{file}", methods=["GET"])
async def convert(request):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "Pending"}

    file = request.path_params.get("file")
    task = BackgroundTask(m4a_to_mp3, file=file, task_id=task_id, state=tasks)

    return UJSONResponse(
        {"status": app.url_path_for("status", task_id=task_id)}, background=task
    )


@app.route("/status/{task_id}", methods=["GET"])
async def status(request):
    """
    Checks status of task and return result
    when ready
    """
    task_id = request.path_params.get("task_id")
    result = tasks.get(task_id)

    if result is not None and result["status"] is "Pending":
        return UJSONResponse(result)

    del tasks[task_id]
    return UJSONResponse(result)


@app.route("/retrieve/{file}", methods=["GET"])
async def stream_files(request):
    file = request.path_params.get("file")
    return StreamingResponse(
        generate(file),
        headers={
            "content-disposition": f"attachment; filename={file}",
            "content-type": "application/octet-stream",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app)
