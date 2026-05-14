import json
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
        # 1) Health check
        r = client.get("/health/live")
        r.raise_for_status()
        print("Health:", r.json())

        # 2) Create ingestion via URL (works without a local PDF file)
        multipart = {
            "teacherId": (None, "t1"),
            "classId": (None, "c1"),
            "title": (None, "Web Lesson Demo"),
            "url": (None, "https://example.com/"),
        }
        r = client.post("/v1/ingestions", files=multipart)
        r.raise_for_status()
        ingestion = r.json()
        print("Ingestion:", ingestion)

        ingestion_id = ingestion["ingestionId"]

        # 3) Generate quiz from ingestion (explicit generate since auto-gen is only on file uploads)
        payload = {"ingestionId": ingestion_id, "preferences": {}}
        r = client.post("/v1/quizzes/generate", json=payload)
        r.raise_for_status()
        draft = r.json()
        print("Generated quizId:", draft["quizId"], "questions:", len(draft["questions"]))

        quiz_id = draft["quizId"]

        # 4) Fetch review artifact
        r = client.get(f"/v1/quizzes/{quiz_id}/review-export")
        r.raise_for_status()
        review = r.json()
        print("Review quizId:", review["quizId"], "version:", review["version"]) 
        if review["questions"]:
            q = review["questions"][0]
            print("First question:", {"type": q["type"], "topic": q["topic"], "stem": q["stem"][:100]})


if __name__ == "__main__":
    main()
