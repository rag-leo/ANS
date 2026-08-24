from backend.services.retrieval_service import (
    RetrievalService
)

service = RetrievalService()

results = service.search(
    query="Sugarcane news",
    crop="ऊस"
)

for result in results:
    print(result["title"])
    print(result["score"])
    print(result["content"][:200])
    print("-" * 80)


#query="मका दर",
#    crop="मका"    