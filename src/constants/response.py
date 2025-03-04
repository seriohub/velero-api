common_error_authenticated_response = {
    400: {
        "description": "Bad Request - Invalid parameters",
        "content": {"application/json": {
            "example": {"detail": {"title": "title error....", "description": "title description...."}}}}
    },
    401: {
        "description": "Unauthorized - Authentication required",
        "content": {"application/json": {"example": {"detail": "Not authenticated"}}}
    }
}
