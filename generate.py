import json
import os
import shutil
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

SCID = "1a2b3c4d-0000-0000-0000-00000000aaaa"
SCID2 = "5e6f7a8b-0000-0000-0000-00000000bbbb"
PID = "0-12345"
AVATAR = "0,moco_support_cat,#1D1D1D,#878787"
LINK = "https://link.example.com"
NOW_MS = 1792700000000

BEARER = "Authorization: Bearer <identity JWT>"
BEARER_SOFT = "Authorization: Bearer <identity JWT> (optional; game account id and player name are read from it)"
NONE = "none"
WS_AUTH = "websocket"


def ok(data=None, **extra):
    r = {"ok": True}
    if data is not None:
        r["data"] = data
    r.update(extra)
    return r


def err(*codes):
    return {"shape": {"ok": False, "error": "<code>"}, "codes": list(codes)}


avail = [{"system": "laser", "deeplink": f"{LINK}/"}]


def connected():
    return [{
        "system": "laser", "application": "laser-prod", "username": "PlayerName",
        "progress": ["1500", "0"], "score": 1500,
        "seasonPassActive": False, "seasonPassType": "DEFAULT", "seasonPassProgress": 0,
        "applicationAccountId": PID,
    }]


def profile(public=False, rel=None):
    p = {
        "universalLink": f"{LINK}/?supercell_id&p={SCID}",
        "name": {"name": "PlayerName", "changeAllowed": NOW_MS + 86400000 * 30},
        "avatarImage": AVATAR if public else {"image": AVATAR},
        "profileImage": AVATAR,
    }
    if rel:
        p["relationship"] = {"status": rel, "timestamp": NOW_MS}
    p.update({
        "qrCodeURL": f"{LINK}/?supercell_id&p={SCID}",
        "forcedOfflineStatus": False,
        "blockIncomingFriendRequests": False,
        "supportTier": 1,
        "scid": SCID,
        "accountId": SCID,
        "handle": {"id": "PlayerHandle", "isChangeAllowed": True},
        "availableSystems": avail,
        "connectedSystems": connected(),
        "characterClass": "connected_games_multi",
        "identifier": {"type": "EMAIL", "value": "player@example.com", "scid_id": SCID},
        "featurePermissions": {},
    })
    return p


def friend(rel="FRIEND"):
    return {
        "accountId": SCID2, "handle": "FriendHandle", "name": "FriendName",
        "profileImage": AVATAR, "gameAccountId": 67890, "playerName": "FriendInGame",
        "scid": SCID2, "avatarImage": AVATAR, "applicationAccountId": "0-67890",
        "relationship": {"status": rel, "timestamp": NOW_MS},
        "availableSystems": avail, "connectedSystems": ["laser"],
    }


def item(status="AVAILABLE", claim=None, title="GIFT!!!", sp=False):
    pid = "com.supercell.laser.scid.seasonpass.basic" if sp else "com.supercell.laser.scid.specialoffertier0.free.item_abc123"
    return {
        "id": "item_abc123", "type": "SEASON_PASS" if sp else "UNKNOWN", "tier": "DEFAULT",
        "origin": "STORE_FREE_OFFER_CLAIM", "accountId": SCID, "createdAt": NOW_MS,
        "status": {"status": status, "timestamp": NOW_MS, "claimToken": claim},
        "productId": pid,
        "receiptId": f"SUPERCELL_STORE_FREE_OFFER_CLAIM:{SCID}#{pid}#1",
        "applications": ["laser-prod"] if status == "CLAIM_IN_PROGRESS" else ["laser", "laser-prod"],
        "contents": {"BrawlPass": 1} if sp else {"Gems": 100},
        "title": title if status == "AVAILABLE" else None,
    }


session = profile()
session.update({
    "friends": [friend()],
    "friendRequests": [friend("REQUEST_RECEIVED"), friend("REQUEST_SENT")],
    "outgoingRequests": [friend("REQUEST_SENT")],
    "incomingFriendRequestsCount": 1,
    "ctaCampaigns": [],
    "isQuarantined": False,
    "sp": {"allowed": False},
    "items": [item()],
})


def friends_list(public=False):
    if public:
        return ok({"friends": [friend("STRANGER")], "outgoingRequests": [], "incomingRequests": [],
                   "friendRequests": [], "incomingFriendRequestsCount": 0})
    return ok({"friends": [friend(), friend("REQUEST_RECEIVED"), friend("REQUEST_SENT")],
               "outgoingRequests": [friend("REQUEST_SENT")],
               "incomingRequests": [friend("REQUEST_RECEIVED")],
               "friendRequests": [friend("REQUEST_RECEIVED"), friend("REQUEST_SENT")],
               "incomingFriendRequestsCount": 1})


basic_public = {
    "accountId": SCID2, "profileImage": AVATAR, "handle": "FriendHandle", "name": "FriendName",
    "playerName": "FriendName", "gameAccountId": 67890, "scid": SCID2,
    "applicationAccountId": "0-67890", "avatarImage": AVATAR, "availableSystems": avail,
    "connectedSystems": [{"system": "laser", "application": "laser-prod", "username": "FriendName",
                          "progress": ["0", "0"], "score": 0, "seasonPassActive": False,
                          "applicationAccountId": "0-67890"}],
    "relationship": {"status": "STRANGER"},
}

E = []


def ep(group, name, method, path, auth, request, response, errors=None, notes=None, extra=None):
    spec = {"method": method, "path": path, "auth": auth, "request": request, "response": response}
    if errors:
        spec["errors"] = errors
    if notes:
        spec["notes"] = notes
    if extra:
        spec.update(extra)
    E.append((group, name, spec))


def form(**fields):
    return {"contentType": "application/x-www-form-urlencoded", "fields": fields}


ep("wellknown", "jwks", "GET", "/.well-known/jwks.json", NONE, None,
   {"keys": [{"kty": "EC", "use": "sig", "crv": "P-256", "kid": "<kid>", "alg": "ES256",
              "x": "<base64url X>", "y": "<base64url Y>"}]})

ep("social", "session.init", "POST", "/api/social/v3/session.init", BEARER, form(),
   ok(session), err("login_expired (HTTP 401, no token)", "token_revoked (HTTP 401)"),
   notes="Own profile: avatarImage is an object {image}. A token whose game account has no SCID profile, "
         "or whose scid no longer matches it, gets token_revoked.")
ep("social", "profile.get", "POST", "/api/social/v3/profile.get", BEARER,
   form(scid="<optional: another player's scid; empty = own profile>"),
   ok(profile()), err("binding_not_found"),
   extra={"responsePublic": ok(profile(public=True, rel="STRANGER"))},
   notes="Own profile: avatarImage is an object {image}. Another player's profile (the .public file): "
         "avatarImage is a plain recipe string and relationship is set "
         "(FRIEND / REQUEST_SENT / REQUEST_RECEIVED / STRANGER).")
ep("social", "profile.setAvatar", "POST", "/api/social/v3/profile.setAvatar", BEARER,
   form(avatarImage="<gradientIndex>,<characterName>,<#color1>,<#color2>"), ok(profile()), err("binding_not_found"),
   notes="characterName must exist in the client's avatar atlas.")
ep("social", "profile.setHandle", "POST", "/api/social/v3/profile.setHandle", BEARER,
   form(handle="PlayerHandle (5-18 chars, [a-zA-Z0-9])"), ok(profile()),
   err("profile_handle_too_short", "profile_handle_too_long", "invalid_handle", "old_handle", "binding_not_found"))
ep("social", "profile.setName", "POST", "/api/social/v3/profile.setName", BEARER,
   form(name="PlayerName (2-20 chars)"), ok(profile()),
   err("profile_name_too_short", "profile_name_too_long", "old_handle", "binding_not_found"))
ep("social", "profile.setForcedOffline", "POST", "/api/social/v3/profile.setForcedOffline", BEARER,
   form(forcedOfflineStatus="true|false"), ok({"forcedOfflineStatus": True}), err("token_revoked"))
ep("social", "profile.setBlockIncomingFriendRequests", "POST",
   "/api/social/v3/profile.setBlockIncomingFriendRequests", BEARER,
   form(blockIncomingFriendRequests="true|false"), ok({"blockIncomingFriendRequests": True}), err("token_revoked"))
ep("social", "profile.generateHandleSuggestions", "POST", "/api/social/v3/profile.generateHandleSuggestions", BEARER,
   form(handle="<optional seed>", name="<optional seed>"),
   ok({"suggestions": ["PlayerName123", "SwiftTiger42", "CosmicFox777", "IronHawk5", "NeonWolf318", "DarkBlade90"]}),
   notes="Each suggestion must satisfy the handle rules (5-18 chars, [a-zA-Z0-9]).")
ep("social", "profiles.list", "POST", "/api/social/v3/profiles.list", BEARER,
   form(handles='["FriendHandle"] (JSON array, optional)', appAccountIds='["0-67890"] (JSON array, optional)'),
   ok({"profiles": [basic_public]}),
   notes="avatarImage is a plain recipe string here.")
ep("social", "friends.list", "POST", "/api/social/v3/friends.list", BEARER,
   form(scid="<optional: another player's scid to list their friends>"), friends_list(),
   extra={"responsePublic": friends_list(True)},
   notes="Own list: friends must contain every relation (friends, incoming and outgoing requests); the client "
         "splits it by relationship.status. connectedSystems is an array of strings; objects break the client parser.")
ep("social", "friends.createRequest", "POST", "/api/social/v3/friends.createRequest", BEARER,
   form(scids=f'["{SCID2}"] (JSON array or a single scid)'),
   ok({"scids": {SCID2: {"ok": True}}, "appAccounts": {}}), err("binding_not_found"),
   notes="scids maps each requested scid to its result.")
ep("social", "friends.acceptRequest", "POST", "/api/social/v3/friends.acceptRequest", BEARER,
   form(scids=f'["{SCID2}"]'), ok({}))
for n in ["friends.deleteRequest", "friends.delete", "friends.remove"]:
    ep("social", n, "POST", f"/api/social/v3/{n}", BEARER,
       form(scid=SCID2, scids=f'["{SCID2}"] (JSON array or comma-separated)'), ok({}),
       err("missing_required_data (HTTP 400)"),
       notes="friends.deleteRequest, friends.delete and friends.remove behave the same.")

ep("inventory", "items.list", "POST", "/api/inventory/v3/items.list", BEARER, form(),
   ok({"items": [item(), item(sp=True)]}), err("token_revoked (HTTP 401)"),
   notes="status is DONATION_RECEIVED for a Brawl Pass gifted by another player and not yet accepted.")
ep("inventory", "items.claim", "POST", "/api/inventory/v3/items.claim", BEARER,
   form(productId="com.supercell.laser.scid.specialoffertier0.free.item_abc123"),
   ok({"item": item("CLAIM_IN_PROGRESS", claim="<claim JWT>")}),
   err("token_revoked (HTTP 401)", "not_found", "claim_failed"))
ep("inventory", "items.claimComplete", "POST", "/api/inventory/v3/items.claimComplete", BEARER,
   form(token="<claim JWT from items.claim>"), ok(),
   err("invalid_claim_token (HTTP 401)", "claim_failed"),
   notes="The response has no data field.")
ep("inventory", "items.donate", "POST", "/api/inventory/v3/items.donate", BEARER,
   form(receiverAccountId="0-67890 or the receiver's scid", productId="com.supercell.laser.scid.seasonpass.basic",
        itemId="item_abc123"),
   ok({"item": item("DONATION_SENT", sp=True)}), err("receiver_not_found", "item_not_available"),
   notes="Only Brawl Pass items can be gifted.")
ep("inventory", "items.accept", "POST", "/api/inventory/v3/items.accept", BEARER,
   form(itemId="item_abc123", productId="<optional>"), ok({"item": item("AVAILABLE", sp=True)}),
   err("donation_not_found"))
ep("inventory", "items.reject", "POST", "/api/inventory/v3/items.reject", BEARER,
   form(itemId="item_abc123", productId="<optional>"), ok({"item": item("DONATION_REJECTED", sp=True)}),
   err("donation_not_found"))

for p in ["/api/security/sessionToken", "/api/security/v1/sessionToken", "/api/security/v2/sessionToken"]:
    ep("security", p.split("/api/security/")[1].replace("/", "_"), "GET|POST", p, BEARER, None,
       ok(token="<session JWT>"), err("login_expired (HTTP 401)", "token_revoked (HTTP 401)"),
       notes="token is at the top level, not inside data.")

ep("ingame", "getConfig", "POST", "/api/ingame/account/getConfig", BEARER, form(),
   ok({"language": "en", "game": "laser", "playerRegion": "", "gameAccountNickname": "",
       "gameAccountToken": "<account JWT or empty>", "gameHelpLink": "", "reCaptchaKey": "",
       "environment": "prod", "gameSeasonName": "", "versionSuffix": ""}))
ep("ingame", "settings.get", "POST", "/api/ingame/account/settings.get", BEARER, form(),
   ok({"created": "2026-01-01T00:00:00.0000000+00:00", "lang": "en", "email_marketing_permission": False,
       "email_marketing_timestamp": "0", "marketing_scope_consents": [], "email_retargeting_permission": False}))
ep("ingame", "settings.set", "POST", "/api/ingame/account/settings.set", BEARER,
   form(accept_marketing="true|false"), ok({"accept_marketing": True}), err("token_revoked (HTTP 401)"))
ep("ingame", "create", "POST", "/api/ingame/account/create", BEARER_SOFT,
   form(email="player@example.com"), ok({"email": "player@example.com", "state": "pending"}),
   err("invalid_email_address", "throttled (HTTP 429)", "generic (email belongs to another account)",
       "server (HTTP 502)"),
   notes="Sends a PIN to the email.")
ep("ingame", "create.confirm", "POST", "/api/ingame/account/create.confirm", BEARER_SOFT,
   form(email="player@example.com", pin="123456"),
   ok({"scidToken": "<account JWT>", "bindToken": "<account JWT>", "refreshToken": "<base64, 32 bytes>"}),
   err("incorrect_pin", "generic", "rebinding_same_game"),
   notes="If the email is already bound to the same game account, this behaves as login.confirm "
         "(the response also carries switchAccount and requiresReconnect).")
ep("ingame", "login", "POST", "/api/ingame/account/login", BEARER_SOFT,
   form(email="player@example.com"), ok({"email": "player@example.com", "state": "pending"}),
   err("missing_required_data", "invalid_email_address", "throttled (HTTP 429)", "server (HTTP 502)"),
   notes="Sends a PIN to the email.")
ep("ingame", "login.validate", "POST", "/api/ingame/account/login.validate", BEARER_SOFT,
   form(email="player@example.com", pin="123456"), ok({"isBound": True}), err("incorrect_pin"),
   notes="Must not consume the PIN: login.confirm verifies the same PIN afterwards. "
         "isBound is false when the email has no game account bound yet.")
ep("ingame", "login.confirm", "POST", "/api/ingame/account/login.confirm", BEARER_SOFT,
   form(email="player@example.com", pin="123456"),
   ok({"scidToken": "<account JWT>", "bindToken": "<account JWT>", "refreshToken": "<base64, 32 bytes>",
       "switchAccount": False, "requiresReconnect": False}),
   err("missing_required_data", "incorrect_pin", "binding_not_found", "rebinding_same_game"),
   notes="The Android client may send this request 2-3 times in parallel; repeats should get the same response. "
         "switchAccount / requiresReconnect are true when the email belongs to a different game account.")

ep("account", "accounts.batchGetByAccountTokens", "POST", "/api/account/v2/accounts.batchGetByAccountTokens", NONE,
   form(accountTokens='["<account JWT>", ...] (or accountToken*=..., or a raw JSON array as the body)'),
   ok({"<account JWT>": ok({
       "scid": SCID, "identifier": {"type": "EMAIL", "value": "player@example.com"},
       "connectedSystem": {"application": "laser-prod", "applicationAccountId": PID,
                           "applicationAccountAlias": "PlayerHandle", "username": "PlayerName",
                           "progress": ["1500", "1500"], "score": 1500, "seasonPassActive": False},
       "applications": [{"application": "laser-prod", "account": {"id": PID, "alias": "PlayerHandle",
                         "name": "PlayerName", "progress": ["1500", "1500"], "score": 1500}}],
       "name": "PlayerName", "avatarImage": AVATAR, "handle": "PlayerHandle"})}),
   notes="data maps each account token to its profile.")
ep("account", "pinAuthentication.start", "POST", "/api/account/v2/pinAuthentication.start", BEARER_SOFT,
   form(scope="<path of the scope endpoint to call next>", identifier="player@example.com (empty = email from the JWT)"),
   ok({"state": "0123456789abcdef0123456789abcdef"}), err("invalid_email_address", "server (HTTP 502)"),
   notes="Sends a PIN to the email.")
ep("account", "pinAuthentication.complete", "POST", "/api/account/v2/pinAuthentication.complete", NONE,
   form(state="0123456789abcdef0123456789abcdef", pin="123456"),
   ok({"authentication": {"scope": "<scope from pinAuthentication.start>", "token": "0123456789abcdef0123456789abcdef"}}),
   err("login_expired (unknown state)", "incorrect_pin"))
ep("account", "recoveryCodes.generate", "POST", "/api/account/v2/recoveryCodes.generate", NONE, form(),
   ok({"codes": ["ABCD-EFGH", "JKLM-NPQR", "STUV-WXYZ", "2345-6789", "AB23-CD45",
                 "EF67-GH89", "JK23-LM45", "NP67-QR89", "ST23-UV45", "WX67-YZ89"],
       "token": "0123456789abcdef0123456789abcdef"}),
   notes="10 codes in XXXX-XXXX format.")
for p in ["/api/account/v2/account/recoveryIdentifier.link", "/api/account/v2/account/accountProtection.modify",
          "/api/account/v2/account/accountProtection.disable", "/api/account/v2/account/identifier.link",
          "/api/account/v2/account/identifier.change", "/api/account/recoveryIdentifier.link",
          "/api/account/accountProtection.modify", "/api/account/accountProtection.disable",
          "/api/account/identifier.link", "/api/account/identifier.change"]:
    name = ("v2_" if "/v2/" in p else "legacy_") + p.rsplit("/", 1)[1]
    ep("account/scope", name, "POST", p, NONE, form(),
       ok({"token": "0123456789abcdef0123456789abcdef"}),
       notes="Called after pinAuthentication.complete with the scope it returned.")

ep("event", "notification.ack", "POST", "/api/event/v1/notification.ack", BEARER,
   form(event="dismiss|...", token="<claim JWT>"), {"ok": True},
   notes="event=dismiss with the claim JWT is sent when the player presses OKAY on an Items Delivered card.")

ep("laser", "profile", "GET", "/laser/{hi}-{lo}", NONE, None,
   {"account_id": "profile:12345", "handle": "PlayerName", "image_ref": "<image reference>",
    "game_account_id": "0-12345", "request_friend_deeplink": "<deeplink>", "allow_update": True},
   err("not_found (HTTP 400)"),
   extra={"responseAnonymous": {"account_id": "anonymous:laser:0-12345", "handle": "ShadowWolf123",
                                "image_ref": "player_icon_maisie_bizarre", "game_account_id": "0-12345",
                                "request_friend_deeplink": "", "allow_update": False}},
   notes="No ok/data wrapper. A game account without an SCID profile gets the .anonymous card.")
ep("cdn", "assets", "GET", "/cdn/assets/{*assetPath}", NONE, None, None,
   notes="Binary proxy to https://cdn.id.supercell.com/assets/{assetPath}. Errors are a bare HTTP status.",
   extra={"bodyNote": "binary asset"})
ep("ws", "purchases-received", "GET (WebSocket)", "/ws", WS_AUTH, None,
   {"notification": {
        "issuedAt": {"seconds": 1792700000}, "notBefore": {"seconds": 1792700000},
        "purchasesReceived": {
            "product": {"application": "laser", "imageUrl": "<url>", "backgroundImageUrl": "<url>",
                        "logoImageUrl": "<url>", "priority": 100000, "type": "<product type>",
                        "title": {"en": "GIFT!!!"}, "tags": ["STORE_FREE_OFFER_CLAIM"]},
            "productQuantity": 1, "token": "<claim JWT>", "templateType": 1, "groupId": "<group id>",
            "origin": "STORE_FREE_OFFER_CLAIM",
            "shopItems": [{"id": "item_abc123",
                           "productId": "com.supercell.laser.scid.specialoffertier0.free.item_abc123",
                           "type": "UNKNOWN", "tier": "DEFAULT", "status": {"available": {}},
                           "applications": ["laser", "laser-prod"],
                           "contents": [{"key": "Gems", "value": 100}]}]}}},
   notes="The server pushes binary protobuf ServerMessage{Notification{PurchasesReceived}} frames (Items "
         "Delivered cards); the file shows one decoded frame. An invalid token is rejected with HTTP 401 "
         "before the upgrade; a revoked session is closed with PolicyViolation.",
   extra={"bodyNote": "protobuf frames"})

for entry in os.listdir(OUT):
    path = os.path.join(OUT, entry)
    if os.path.isdir(path):
        shutil.rmtree(path)

GROUPS = {
    "wellknown": "Well-known",
    "social": "Social",
    "inventory": "Inventory",
    "security": "Security",
    "ingame": "In-game account",
    "account": "Account",
    "account/scope": "Account protection steps",
    "event": "Events",
    "laser": "Profile card",
    "cdn": "CDN",
    "ws": "WebSocket",
}

AUTH_LABELS = {
    BEARER: "Bearer",
    BEARER_SOFT: "Bearer, optional",
    NONE: "-",
    WS_AUTH: "Bearer, `?token=` or first message",
}


def text(s):
    return s.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def request_cell(request):
    if not request or not request["fields"]:
        return "-"
    return "<br>".join(f"`{name}`: {text(desc)}" for name, desc in request["fields"].items())


def errors_cell(errors):
    if not errors:
        return "-"
    cells = []
    for code in errors["codes"]:
        head, _, tail = code.partition(" ")
        cells.append(f"`{head}`" + (f" {text(tail)}" if tail else ""))
    return "<br>".join(cells)


def write_body(rel_path, body):
    full = os.path.join(OUT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False, indent=2)
        f.write("\n")


rows = {group: [] for group in GROUPS}
notes = {group: [] for group in GROUPS}
files_written = 0
for group, name, spec in E:
    links = []
    if spec["response"] is not None:
        rel = f"{group}/{name}.json"
        write_body(rel, spec["response"])
        links.append(f"[{name}.json]({rel})")
        files_written += 1
    for key, body in spec.items():
        if key.startswith("response") and key != "response":
            variant = key[len("response"):].lower()
            rel = f"{group}/{name}.{variant}.json"
            write_body(rel, body)
            links.append(f"[{name}.{variant}.json]({rel})")
            files_written += 1
    if spec.get("bodyNote"):
        links.insert(0, text(spec["bodyNote"]))

    rows[group].append("| {} | `{}` | {} | {} | {} | {} |".format(
        text(spec["method"]), spec["path"], AUTH_LABELS[spec["auth"]],
        request_cell(spec["request"]), errors_cell(spec.get("errors")), "<br>".join(links)))
    if spec.get("notes"):
        notes[group].append(f"- `{spec['path']}`: {text(spec['notes'])}")

with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
    f.write("# Supercell ID endpoints\n\n")
    f.write("Response bodies of the Supercell ID HTTP API as the Brawl Stars client (v59) uses it. "
            "All values are placeholders.\n\n")
    f.write("- Each JSON file is the body of a successful response. Some endpoints have a second variant "
            "next to it (`*.public.json`, `*.anonymous.json`).\n")
    f.write("- Requests are form-encoded (`application/x-www-form-urlencoded`); the Request column lists the fields.\n")
    f.write("- Auth: **Bearer** is `Authorization: Bearer <identity JWT>` (an account or session token); "
            "**Bearer, optional** is sent when the client has a token and tells which game account the call is for.\n")
    f.write("- Errors share one shape, `{\"ok\": false, \"error\": \"<code>\"}`, with HTTP 200 unless noted.\n")
    f.write("- Regenerate with `python3 generate.py`.\n")
    for group, title in GROUPS.items():
        if not rows[group]:
            continue
        f.write(f"\n## {title}\n\n")
        f.write("| Method | Path | Auth | Request | Errors | Response |\n|---|---|---|---|---|---|\n")
        f.write("\n".join(rows[group]) + "\n")
        if notes[group]:
            f.write("\n" + "\n".join(notes[group]) + "\n")

print(f"{len(E)} endpoints, {files_written} response files written to {OUT}")
