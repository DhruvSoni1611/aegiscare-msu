import requests
import streamlit as st

API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000")
SESSION_HEADER = "X-Session-Id"


def _headers():
    h = {}
    sid = st.session_state.get("session_id")
    if sid:
        h[SESSION_HEADER] = sid
    return h


def post(path, json=None, files=None):
    return requests.post(f"{API_BASE}{path}", json=json, files=files, headers=_headers(), timeout=60)


def get(path, params=None):
    return requests.get(f"{API_BASE}{path}", params=params, headers=_headers(), timeout=60)
