from fastapi import Request
from typing import Optional, Dict, Any

class SessionService:
    def __init__(self, request: Request):
        self.request = request

    def get_user_id(self) -> Optional[int]:
        # Retrieves the current user's ID from the session
        return self.request.session.get("user_id")

    def get_username(self) -> Optional[str]:
        # Retrieves the current user's username from the session
        return self.request.session.get("username")

    def set_user_session(self, user_id: int, username: str) -> None:
        # Stores user ID and username in the session
        self.request.session["user_id"] = user_id
        self.request.session["username"] = username

    def clear_session(self) -> None:
        # Removes all data from the current session
        self.request.session.clear()

    def get_template_data(self, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        # Returns template data including session info and any additional data
        data = {
            "request": self.request,
            "user_id": self.get_user_id(),
            "username": self.get_username()
        }
        if additional_data:
            data.update(additional_data)
        return data 