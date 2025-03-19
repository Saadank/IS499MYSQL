from fastapi import Request
from typing import Optional, Dict, Any

class SessionService:
    def __init__(self, request: Request):
        self.request = request

    def get_user_id(self) -> Optional[int]:
        return self.request.session.get("user_id")

    def get_username(self) -> Optional[str]:
        return self.request.session.get("username")

    def set_user_session(self, user_id: int, username: str) -> None:
        self.request.session["user_id"] = user_id
        self.request.session["username"] = username

    def clear_session(self) -> None:
        self.request.session.clear()

    def get_template_data(self, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        data = {
            "request": self.request,
            "user_id": self.get_user_id(),
            "username": self.get_username()
        }
        if additional_data:
            data.update(additional_data)
        return data 