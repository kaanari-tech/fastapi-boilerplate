import logging
from pathlib import Path
import random
import time
from typing import Optional

from fastapi import FastAPI, Response
import httpx
import uvicorn
from opentelemetry.propagate import inject

from backend.core.conf import settings
from backend.core.registrar import register_app
from backend.app.api import (admin_router)
from backend.utils.prometheus import EndpointFilter, setting_otlp


app = FastAPI()

setting_otlp(app, settings.APP_NAME, settings.OTLP_GRPC_ENDPOINT)
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@app.get("/")
async def read_root():
    logging.error("Hello World")
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    logging.error("items")
    return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
    time.sleep(1)
    logging.error("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
    for i in range(1000):
        _ = i * i * i
    logging.error("cpu task")
    return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
    response.status_code = random.choice([200, 200, 300, 400, 500])
    logging.error("random status")
    return {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
    time.sleep(random.randint(0, 5))
    logging.error("random sleep")
    return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
    logging.error("got error!!!!")
    raise ValueError("value error")


@app.get("/chain")
async def chain(response: Response):
    headers = {}
    inject(headers)  # inject trace info to header
    logging.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://api_v2:8000/io_task",
            headers=headers,
        )
    # async with httpx.AsyncClient() as client:
    #     await client.get(
    #         f"http://api_v2:8000/cpu_task",
    #         headers=headers,
    #     )
    logging.info("Chain Finished")
    return {"path": "/chain"}


app.mount("/admin", register_app(admin_router, "admin"))



if __name__ == '__main__':
    # If you like to DEBUG in the IDE, the main startup method is very helpful.
    # If you like to debug via print, it is recommended to use the fastapi cli method to start the service.
    # try:
    #     config = uvicorn.Config(app=f'{Path(__file__).stem}:app', reload=True)
    #     server = uvicorn.Server(config)
    #     server.run()
    # except Exception as e:
    #     raise e
    
    # update uvicorn access logger format
    log_config = uvicorn.config.LOGGING_CONFIG
    print("---> ", log_config)
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=log_config)
