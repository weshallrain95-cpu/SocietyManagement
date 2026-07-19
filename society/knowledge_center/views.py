from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .loader import load_knowledge
from .save_note import save_note
from .remove_focus import remove_focus


def knowledge_center(request):
    """
    Returns the complete Knowledge Center.
    """

    return JsonResponse(load_knowledge())


@csrf_exempt
def knowledge_center_save(request):
    """
    Persists one knowledge note.
    """

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required.",
            },
            status=405,
        )

    payload = json.loads(request.body)

    saved_note = save_note(

        category=payload["category"],

        note={

            "title": payload["title"],

            "summary": payload["summary"],

            "details": payload["details"],

            "status": payload.get(
                "status",
                "FROZEN",
            ),

            "makeCurrentFocus": payload.get(
                "makeCurrentFocus",
                False,
            ),

        },

    )

    return JsonResponse(

        {

            "success": True,

            "note": saved_note,

        }

    )

@csrf_exempt
def knowledge_center_remove_focus(request):
    """
    Removes one note from the Active Focus board.
    """

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required.",
            },
            status=405,
        )

    payload = json.loads(request.body)

    remove_focus(
        payload["note_id"],
    )

    return JsonResponse(
        {
            "success": True,
        }
    )

    