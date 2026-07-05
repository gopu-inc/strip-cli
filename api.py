# api.py
"""Client HTTP pour l'API STRIP"""

import requests
from typing import Optional, Dict, Any, List
from pathlib import Path

from config import Config


class APIClient:
    """Client HTTP pour l'API STRIP"""

    def __init__(self):
        self.config = Config()
        self.base_url = self.config.get("api_url", "https://hoosthubs-g.onrender.com")
        self.timeout = self.config.get("timeout", 30)

    # ─── Requêtes génériques ───────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        token: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Optional[Any]:
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            if method == "GET":
                response = requests.get(
                    url, headers=headers, timeout=self.timeout, params=params
                )
            elif method == "POST":
                if files:
                    response = requests.post(
                        url, data=data, files=files, headers=headers, timeout=self.timeout
                    )
                else:
                    response = requests.post(
                        url, json=data, headers=headers, timeout=self.timeout
                    )
            elif method == "PUT":
                response = requests.put(
                    url, json=data, headers=headers, timeout=self.timeout
                )
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return None

            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            return None
        except Exception:
            return None

    def get(
        self,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Optional[Any]:
        return self._request("GET", endpoint, token=token, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        token: Optional[str] = None,
    ) -> Optional[Any]:
        return self._request("POST", endpoint, data=data, files=files, token=token)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        token: Optional[str] = None,
    ) -> Optional[Any]:
        return self._request("PUT", endpoint, data=data, token=token)

    def delete(self, endpoint: str, token: Optional[str] = None) -> Optional[Any]:
        return self._request("DELETE", endpoint, token=token)

    # ─── Authentification ──────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> Optional[Dict]:
        try:
            response = requests.post(
                f"{self.base_url}/api/token",
                data={"username": username, "password": password},
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def register(self, username: str, password: str, email: str = "") -> Optional[Dict]:
        return self.post(
            "/api/users/register",
            data={"username": username, "password": password, "email": email or None},
        )

    # ─── Profil ────────────────────────────────────────────────────────────────

    def get_my_profile(self, token: str) -> Optional[Dict]:
        return self.get("/api/users/me", token=token)

    def get_user_profile(
        self, user_id: str, token: Optional[str] = None
    ) -> Optional[Dict]:
        return self.get(f"/api/users/{user_id}", token=token)

    def get_profile_full(
        self, user_id: str, token: Optional[str] = None
    ) -> Optional[Dict]:
        return self.get(f"/api/profile/{user_id}/full", token=token)

    def update_profile(self, data: Dict, token: str) -> Optional[Dict]:
        return self.put("/api/users/me", data=data, token=token)

    def follow_user(self, user_id: str, token: str) -> Optional[Dict]:
        return self.post(f"/api/users/{user_id}/follow", token=token)

    def get_verification_status(self, token: str) -> Optional[Dict]:
        return self.get("/api/users/me/verification-status", token=token)

    # ─── Feed / Vidéos ─────────────────────────────────────────────────────────

    def get_feed(self, token: Optional[str] = None, limit: int = 20) -> Optional[List]:
        return self.get(f"/api/feed?limit={limit}", token=token)

    def like_video(self, video_id: str, token: str) -> Optional[Dict]:
        return self.post(f"/api/videos/{video_id}/like", token=token)

    def increment_view(self, video_id: str) -> None:
        self.post(f"/api/videos/{video_id}/view")

    # ─── Chat / Messages ───────────────────────────────────────────────────────

    def get_conversations(self, token: str) -> Optional[List]:
        return self.get("/api/messages/conversations", token=token)

    def get_messages(
        self, user_id: str, token: str, limit: int = 50
    ) -> Optional[List]:
        return self.get(f"/api/messages/{user_id}?limit={limit}", token=token)

    def send_message(
        self, receiver_id: str, content: str, msg_type: str = "text", token: str = ""
    ) -> Optional[Dict]:
        return self.post(
            "/api/messages/send",
            data={"receiver_id": receiver_id, "content": content, "type": msg_type},
            token=token,
        )

    # ─── Sounds ────────────────────────────────────────────────────────────────

    def get_recommended_sounds(
        self, token: Optional[str] = None, limit: int = 30
    ) -> Optional[List]:
        return self.get(f"/api/sounds/recommendations?limit={limit}", token=token)

    def get_sounds_by_category(
        self, category: str, token: Optional[str] = None, limit: int = 20
    ) -> Optional[List]:
        return self.get(
            f"/api/sounds/category/{category}?limit={limit}", token=token
        )

    def like_sound(self, sound_id: str, token: str) -> Optional[Dict]:
        return self.post(f"/api/sounds/{sound_id}/like", token=token)

    def play_sound(self, sound_id: str) -> None:
        self.post(f"/api/sounds/{sound_id}/play")

    def get_sound_details(self, sound_id: str) -> Optional[Dict]:
        return self.get(f"/api/sounds/{sound_id}")

    # ─── Stories ───────────────────────────────────────────────────────────────

    def get_stories(self) -> Optional[List]:
        return self.get("/api/stories")

    # ─── ActFiles ──────────────────────────────────────────────────────────────

    def get_actfiles(self, token: Optional[str] = None, limit: int = 20) -> Optional[List]:
        return self.get(f"/api/actfile?limit={limit}", token=token)

    def like_actfile(self, actfile_id: str, token: str) -> Optional[Dict]:
        return self.post(f"/api/actfile/{actfile_id}/like", token=token)

    def create_actfile(self, content: str, token: str) -> Optional[Dict]:
        return self.post("/api/actfile", data={"content": content}, token=token)

    def get_actfile_comments(self, actfile_id: str) -> Optional[List]:
        return self.get(f"/api/actfile/{actfile_id}/comments")

    def comment_actfile(
        self, actfile_id: str, content: str, token: str
    ) -> Optional[Dict]:
        return self.post(
            f"/api/actfile/{actfile_id}/comment",
            data={"content": content},
            token=token,
        )

    # ─── Lives ─────────────────────────────────────────────────────────────────

    def get_active_lives(self, token: Optional[str] = None) -> Optional[List]:
        return self.get("/api/lives/active", token=token)

    def start_live(
        self,
        title: str,
        description: str = "",
        is_private: bool = False,
        token: str = "",
    ) -> Optional[Dict]:
        return self.post(
            "/api/lives/start",
            data={
                "title": title,
                "description": description,
                "is_private": is_private,
            },
            token=token,
        )

    def stop_live(self, live_id: str, token: str) -> Optional[Dict]:
        return self.post(f"/api/lives/{live_id}/stop", token=token)

    # ─── Notifications ─────────────────────────────────────────────────────────

    def get_notifications(self, token: str, limit: int = 50) -> Optional[List]:
        return self.get(f"/api/notifications?limit={limit}", token=token)

    # ─── Recherche ─────────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        search_type: str = "users",
        token: Optional[str] = None,
        limit: int = 20,
    ) -> Optional[Dict]:
        return self.get(
            f"/api/search?q={query}&type={search_type}&limit={limit}", token=token
        )

    # ─── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self, token: Optional[str] = None) -> Optional[Dict]:
        return self.get("/api/stats", token=token)

    # ─── Upload ────────────────────────────────────────────────────────────────

    def upload_video(
        self,
        file_path: str,
        description: str,
        is_public: bool = True,
        token: str = "",
    ) -> Optional[Dict]:
        if not Path(file_path).exists():
            return None
        with open(file_path, "rb") as f:
            files = {"video": f}
            data = {
                "description": description,
                "is_public": str(is_public).lower(),
            }
            return self.post(
                "/api/videos/upload", data=data, files=files, token=token
            )
