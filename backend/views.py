from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import recommend_songs_from_description

@api_view(["POST"])
def recommend_api(request):
    description = request.data.get("description", "")
    if not description:
        return Response({"error": "No description provided"}, status=400)

    recommendations = recommend_songs_from_description(description)
    return Response({"input": description, "recommendations": recommendations})
