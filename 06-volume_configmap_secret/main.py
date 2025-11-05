import os

PORT = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=PORT)
