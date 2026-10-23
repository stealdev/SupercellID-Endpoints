# Supercell ID endpoints

Response bodies of the Supercell ID HTTP API as the Brawl Stars uses it. All values are placeholders.

- Each JSON file is the body of a successful response. Some endpoints have a second variant next to it (`*.public.json`, `*.anonymous.json`).
- Requests are form-encoded (`application/x-www-form-urlencoded`); the Request column lists the fields.
- Auth: **Bearer** is `Authorization: Bearer <identity JWT>` (an account or session token); **Bearer, optional** is sent when the client has a token and tells which game account the call is for.
- Errors share one shape, `{"ok": false, "error": "<code>"}`, with HTTP 200 unless noted.
- Regenerate with `python3 generate.py`.

## Well-known

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| GET | `/.well-known/jwks.json` | - | - | - | [jwks.json](wellknown/jwks.json) |

## Social

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/social/v3/session.init` | Bearer | - | `login_expired` (HTTP 401, no token)<br>`token_revoked` (HTTP 401) | [session.init.json](social/session.init.json) |
| POST | `/api/social/v3/profile.get` | Bearer | `scid`: &lt;optional: another player's scid; empty = own profile&gt; | `binding_not_found` | [profile.get.json](social/profile.get.json)<br>[profile.get.public.json](social/profile.get.public.json) |
| POST | `/api/social/v3/profile.setAvatar` | Bearer | `avatarImage`: &lt;gradientIndex&gt;,&lt;characterName&gt;,&lt;#color1&gt;,&lt;#color2&gt; | `binding_not_found` | [profile.setAvatar.json](social/profile.setAvatar.json) |
| POST | `/api/social/v3/profile.setHandle` | Bearer | `handle`: PlayerHandle (5-18 chars, [a-zA-Z0-9]) | `profile_handle_too_short`<br>`profile_handle_too_long`<br>`invalid_handle`<br>`old_handle`<br>`binding_not_found` | [profile.setHandle.json](social/profile.setHandle.json) |
| POST | `/api/social/v3/profile.setName` | Bearer | `name`: PlayerName (2-20 chars) | `profile_name_too_short`<br>`profile_name_too_long`<br>`old_handle`<br>`binding_not_found` | [profile.setName.json](social/profile.setName.json) |
| POST | `/api/social/v3/profile.setForcedOffline` | Bearer | `forcedOfflineStatus`: true\|false | `token_revoked` | [profile.setForcedOffline.json](social/profile.setForcedOffline.json) |
| POST | `/api/social/v3/profile.setBlockIncomingFriendRequests` | Bearer | `blockIncomingFriendRequests`: true\|false | `token_revoked` | [profile.setBlockIncomingFriendRequests.json](social/profile.setBlockIncomingFriendRequests.json) |
| POST | `/api/social/v3/profile.generateHandleSuggestions` | Bearer | `handle`: &lt;optional seed&gt;<br>`name`: &lt;optional seed&gt; | - | [profile.generateHandleSuggestions.json](social/profile.generateHandleSuggestions.json) |
| POST | `/api/social/v3/profiles.list` | Bearer | `handles`: ["FriendHandle"] (JSON array, optional)<br>`appAccountIds`: ["0-67890"] (JSON array, optional) | - | [profiles.list.json](social/profiles.list.json) |
| POST | `/api/social/v3/friends.list` | Bearer | `scid`: &lt;optional: another player's scid to list their friends&gt; | - | [friends.list.json](social/friends.list.json)<br>[friends.list.public.json](social/friends.list.public.json) |
| POST | `/api/social/v3/friends.createRequest` | Bearer | `scids`: ["5e6f7a8b-0000-0000-0000-00000000bbbb"] (JSON array or a single scid) | `binding_not_found` | [friends.createRequest.json](social/friends.createRequest.json) |
| POST | `/api/social/v3/friends.acceptRequest` | Bearer | `scids`: ["5e6f7a8b-0000-0000-0000-00000000bbbb"] | - | [friends.acceptRequest.json](social/friends.acceptRequest.json) |
| POST | `/api/social/v3/friends.deleteRequest` | Bearer | `scid`: 5e6f7a8b-0000-0000-0000-00000000bbbb<br>`scids`: ["5e6f7a8b-0000-0000-0000-00000000bbbb"] (JSON array or comma-separated) | `missing_required_data` (HTTP 400) | [friends.deleteRequest.json](social/friends.deleteRequest.json) |
| POST | `/api/social/v3/friends.delete` | Bearer | `scid`: 5e6f7a8b-0000-0000-0000-00000000bbbb<br>`scids`: ["5e6f7a8b-0000-0000-0000-00000000bbbb"] (JSON array or comma-separated) | `missing_required_data` (HTTP 400) | [friends.delete.json](social/friends.delete.json) |
| POST | `/api/social/v3/friends.remove` | Bearer | `scid`: 5e6f7a8b-0000-0000-0000-00000000bbbb<br>`scids`: ["5e6f7a8b-0000-0000-0000-00000000bbbb"] (JSON array or comma-separated) | `missing_required_data` (HTTP 400) | [friends.remove.json](social/friends.remove.json) |

- `/api/social/v3/session.init`: Own profile: avatarImage is an object {image}. A token whose game account has no SCID profile, or whose scid no longer matches it, gets token_revoked.
- `/api/social/v3/profile.get`: Own profile: avatarImage is an object {image}. Another player's profile (the .public file): avatarImage is a plain recipe string and relationship is set (FRIEND / REQUEST_SENT / REQUEST_RECEIVED / STRANGER).
- `/api/social/v3/profile.setAvatar`: characterName must exist in the client's avatar atlas.
- `/api/social/v3/profile.generateHandleSuggestions`: Each suggestion must satisfy the handle rules (5-18 chars, [a-zA-Z0-9]).
- `/api/social/v3/profiles.list`: avatarImage is a plain recipe string here.
- `/api/social/v3/friends.list`: Own list: friends must contain every relation (friends, incoming and outgoing requests); the client splits it by relationship.status. connectedSystems is an array of strings; objects break the client parser.
- `/api/social/v3/friends.createRequest`: scids maps each requested scid to its result.
- `/api/social/v3/friends.deleteRequest`: friends.deleteRequest, friends.delete and friends.remove behave the same.
- `/api/social/v3/friends.delete`: friends.deleteRequest, friends.delete and friends.remove behave the same.
- `/api/social/v3/friends.remove`: friends.deleteRequest, friends.delete and friends.remove behave the same.

## Inventory

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/inventory/v3/items.list` | Bearer | - | `token_revoked` (HTTP 401) | [items.list.json](inventory/items.list.json) |
| POST | `/api/inventory/v3/items.claim` | Bearer | `productId`: com.supercell.laser.scid.specialoffertier0.free.item_abc123 | `token_revoked` (HTTP 401)<br>`not_found`<br>`claim_failed` | [items.claim.json](inventory/items.claim.json) |
| POST | `/api/inventory/v3/items.claimComplete` | Bearer | `token`: &lt;claim JWT from items.claim&gt; | `invalid_claim_token` (HTTP 401)<br>`claim_failed` | [items.claimComplete.json](inventory/items.claimComplete.json) |
| POST | `/api/inventory/v3/items.donate` | Bearer | `receiverAccountId`: 0-67890 or the receiver's scid<br>`productId`: com.supercell.laser.scid.seasonpass.basic<br>`itemId`: item_abc123 | `receiver_not_found`<br>`item_not_available` | [items.donate.json](inventory/items.donate.json) |
| POST | `/api/inventory/v3/items.accept` | Bearer | `itemId`: item_abc123<br>`productId`: &lt;optional&gt; | `donation_not_found` | [items.accept.json](inventory/items.accept.json) |
| POST | `/api/inventory/v3/items.reject` | Bearer | `itemId`: item_abc123<br>`productId`: &lt;optional&gt; | `donation_not_found` | [items.reject.json](inventory/items.reject.json) |

- `/api/inventory/v3/items.list`: status is DONATION_RECEIVED for a Brawl Pass gifted by another player and not yet accepted.
- `/api/inventory/v3/items.claimComplete`: The response has no data field.
- `/api/inventory/v3/items.donate`: Only Brawl Pass items can be gifted.

## Security

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| GET\|POST | `/api/security/sessionToken` | Bearer | - | `login_expired` (HTTP 401)<br>`token_revoked` (HTTP 401) | [sessionToken.json](security/sessionToken.json) |
| GET\|POST | `/api/security/v1/sessionToken` | Bearer | - | `login_expired` (HTTP 401)<br>`token_revoked` (HTTP 401) | [v1_sessionToken.json](security/v1_sessionToken.json) |
| GET\|POST | `/api/security/v2/sessionToken` | Bearer | - | `login_expired` (HTTP 401)<br>`token_revoked` (HTTP 401) | [v2_sessionToken.json](security/v2_sessionToken.json) |

- `/api/security/sessionToken`: token is at the top level, not inside data.
- `/api/security/v1/sessionToken`: token is at the top level, not inside data.
- `/api/security/v2/sessionToken`: token is at the top level, not inside data.

## In-game account

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/ingame/account/getConfig` | Bearer | - | - | [getConfig.json](ingame/getConfig.json) |
| POST | `/api/ingame/account/settings.get` | Bearer | - | - | [settings.get.json](ingame/settings.get.json) |
| POST | `/api/ingame/account/settings.set` | Bearer | `accept_marketing`: true\|false | `token_revoked` (HTTP 401) | [settings.set.json](ingame/settings.set.json) |
| POST | `/api/ingame/account/create` | Bearer, optional | `email`: player@example.com | `invalid_email_address`<br>`throttled` (HTTP 429)<br>`generic` (email belongs to another account)<br>`server` (HTTP 502) | [create.json](ingame/create.json) |
| POST | `/api/ingame/account/create.confirm` | Bearer, optional | `email`: player@example.com<br>`pin`: 123456 | `incorrect_pin`<br>`generic`<br>`rebinding_same_game` | [create.confirm.json](ingame/create.confirm.json) |
| POST | `/api/ingame/account/login` | Bearer, optional | `email`: player@example.com | `missing_required_data`<br>`invalid_email_address`<br>`throttled` (HTTP 429)<br>`server` (HTTP 502) | [login.json](ingame/login.json) |
| POST | `/api/ingame/account/login.validate` | Bearer, optional | `email`: player@example.com<br>`pin`: 123456 | `incorrect_pin` | [login.validate.json](ingame/login.validate.json) |
| POST | `/api/ingame/account/login.confirm` | Bearer, optional | `email`: player@example.com<br>`pin`: 123456 | `missing_required_data`<br>`incorrect_pin`<br>`binding_not_found`<br>`rebinding_same_game` | [login.confirm.json](ingame/login.confirm.json) |

- `/api/ingame/account/create`: Sends a PIN to the email.
- `/api/ingame/account/create.confirm`: If the email is already bound to the same game account, this behaves as login.confirm (the response also carries switchAccount and requiresReconnect).
- `/api/ingame/account/login`: Sends a PIN to the email.
- `/api/ingame/account/login.validate`: Must not consume the PIN: login.confirm verifies the same PIN afterwards. isBound is false when the email has no game account bound yet.
- `/api/ingame/account/login.confirm`: The Android client may send this request 2-3 times in parallel; repeats should get the same response. switchAccount / requiresReconnect are true when the email belongs to a different game account.

## Account

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/account/v2/accounts.batchGetByAccountTokens` | - | `accountTokens`: ["&lt;account JWT&gt;", ...] (or accountToken*=..., or a raw JSON array as the body) | - | [accounts.batchGetByAccountTokens.json](account/accounts.batchGetByAccountTokens.json) |
| POST | `/api/account/v2/pinAuthentication.start` | Bearer, optional | `scope`: &lt;path of the scope endpoint to call next&gt;<br>`identifier`: player@example.com (empty = email from the JWT) | `invalid_email_address`<br>`server` (HTTP 502) | [pinAuthentication.start.json](account/pinAuthentication.start.json) |
| POST | `/api/account/v2/pinAuthentication.complete` | - | `state`: 0123456789abcdef0123456789abcdef<br>`pin`: 123456 | `login_expired` (unknown state)<br>`incorrect_pin` | [pinAuthentication.complete.json](account/pinAuthentication.complete.json) |
| POST | `/api/account/v2/recoveryCodes.generate` | - | - | - | [recoveryCodes.generate.json](account/recoveryCodes.generate.json) |

- `/api/account/v2/accounts.batchGetByAccountTokens`: data maps each account token to its profile.
- `/api/account/v2/pinAuthentication.start`: Sends a PIN to the email.
- `/api/account/v2/recoveryCodes.generate`: 10 codes in XXXX-XXXX format.

## Account protection steps

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/account/v2/account/recoveryIdentifier.link` | - | - | - | [v2_recoveryIdentifier.link.json](account/scope/v2_recoveryIdentifier.link.json) |
| POST | `/api/account/v2/account/accountProtection.modify` | - | - | - | [v2_accountProtection.modify.json](account/scope/v2_accountProtection.modify.json) |
| POST | `/api/account/v2/account/accountProtection.disable` | - | - | - | [v2_accountProtection.disable.json](account/scope/v2_accountProtection.disable.json) |
| POST | `/api/account/v2/account/identifier.link` | - | - | - | [v2_identifier.link.json](account/scope/v2_identifier.link.json) |
| POST | `/api/account/v2/account/identifier.change` | - | - | - | [v2_identifier.change.json](account/scope/v2_identifier.change.json) |
| POST | `/api/account/recoveryIdentifier.link` | - | - | - | [legacy_recoveryIdentifier.link.json](account/scope/legacy_recoveryIdentifier.link.json) |
| POST | `/api/account/accountProtection.modify` | - | - | - | [legacy_accountProtection.modify.json](account/scope/legacy_accountProtection.modify.json) |
| POST | `/api/account/accountProtection.disable` | - | - | - | [legacy_accountProtection.disable.json](account/scope/legacy_accountProtection.disable.json) |
| POST | `/api/account/identifier.link` | - | - | - | [legacy_identifier.link.json](account/scope/legacy_identifier.link.json) |
| POST | `/api/account/identifier.change` | - | - | - | [legacy_identifier.change.json](account/scope/legacy_identifier.change.json) |

- `/api/account/v2/account/recoveryIdentifier.link`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/v2/account/accountProtection.modify`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/v2/account/accountProtection.disable`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/v2/account/identifier.link`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/v2/account/identifier.change`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/recoveryIdentifier.link`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/accountProtection.modify`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/accountProtection.disable`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/identifier.link`: Called after pinAuthentication.complete with the scope it returned.
- `/api/account/identifier.change`: Called after pinAuthentication.complete with the scope it returned.

## Events

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| POST | `/api/event/v1/notification.ack` | Bearer | `event`: dismiss\|...<br>`token`: &lt;claim JWT&gt; | - | [notification.ack.json](event/notification.ack.json) |

- `/api/event/v1/notification.ack`: event=dismiss with the claim JWT is sent when the player presses OKAY on an Items Delivered card.

## Profile card

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| GET | `/laser/{hi}-{lo}` | - | - | `not_found` (HTTP 400) | [profile.json](laser/profile.json)<br>[profile.anonymous.json](laser/profile.anonymous.json) |

- `/laser/{hi}-{lo}`: No ok/data wrapper. A game account without an SCID profile gets the .anonymous card.

## CDN

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| GET | `/cdn/assets/{*assetPath}` | - | - | - | binary asset |

- `/cdn/assets/{*assetPath}`: Binary proxy to https://cdn.id.supercell.com/assets/{assetPath}. Errors are a bare HTTP status.

## WebSocket

| Method | Path | Auth | Request | Errors | Response |
|---|---|---|---|---|---|
| GET (WebSocket) | `/ws` | Bearer, `?token=` or first message | - | - | protobuf frames<br>[purchases-received.json](ws/purchases-received.json) |

- `/ws`: The server pushes binary protobuf ServerMessage{Notification{PurchasesReceived}} frames (Items Delivered cards); the file shows one decoded frame. An invalid token is rejected with HTTP 401 before the upgrade; a revoked session is closed with PolicyViolation.
