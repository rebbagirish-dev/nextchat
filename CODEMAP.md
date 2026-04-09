# NexChat Code Map
> Auto-generated index. Use line numbers to jump directly to any symbol.
> app.py: 500 lines | index.html: 1934 lines (script starts L631)

## app.py — Routes
| Route | L# | Function |
|---|---|---|
| GET / | 246 | index |
| GET /health | 258 | health |
| GET /keep-alive | 262 | keep_alive |
| GET /logged-out | 266 | logged_out |
| POST /login | 270 | login |
| POST /logout | 292 | logout |
| GET /manifest.json | 250 | manifest |
| GET /sw.js | 254 | service_worker |
| GET /api/me | 303 | api_me |
| GET /api/other | 310 | api_other |
| GET /api/messages | 328 | api_messages |
| POST /api/send | 348 | api_send |
| POST /api/typing | 370 | api_typing |
| GET /api/poll | 380 | api_poll |
| POST /api/clear | 397 | api_clear |
| POST /api/call/history/log | 404 | api_call_history_log |
| GET /api/call/history | 424 | api_call_history |
| POST /api/call/history/clear | 440 | api_call_history_clear |
| POST /api/call/signal | 447 | api_call_signal |
| GET /api/call/poll | 469 | api_call_poll |
| POST /api/logout-beacon | 485 | api_logout_beacon |

## app.py — Helper Functions
| Function | L# |
|---|---|
| get_conn / get_cursor | 37 / 42 |
| init_db | 49 |
| ph / phs | 162 / 166 |
| qfetch / qfetchone / qexec / qexec_many | 171 / 179 / 187 / 194 |
| hash_pw / now_ts / now_ts_full / now_dt | 204 / 207 / 212 / 219 |
| is_active | 222 |
| get_user_by_token / require_auth | 231 / 237 |

## index.html — HTML Structure
| Element ID | L# | Purpose |
|---|---|---|
| #login-screen | 344 | Login page |
| #username / #password / #login-btn / #login-error | 370/377/380/379 | Login form |
| #app | 392 | Main app container |
| #xl-ribbon-tabs | 396 | Excel ribbon tabs |
| #other-name | 402 | Other user name in ribbon title |
| #theme-btn / #audio-call-btn / #video-call-btn | 405/406/407 | Desktop ribbon buttons |
| #call-history-btn / #header-clear-btn / #mute-btn | 408/409/410 | Desktop ribbon buttons |
| #menu-dropdown / #menu-btn / #dropdown-menu / #logout-btn | 411/412/413/414 | Desktop ⋮ dropdown |
| #hamburger-dropdown / #hamburger-btn / #hamburger-menu | 418/419/426 | Mobile hamburger |
| #hm-theme-btn / #hm-audio-call-btn / #hm-video-call-btn | 428/429/430 | Hamburger items |
| #hm-call-history-btn / #hm-mute-btn / #hm-clear-btn / #hm-logout-btn | 431/432/433/435 | Hamburger items |
| #xl-cell-ref | 443 | Formula bar cell reference |
| #typing-indicator / #typing-text | 446/448 | Typing indicator |
| #other-status | 450 | Online status in formula bar |
| #fmt-bold / #fmt-italic / #fmt-underline / #fmt-emoji | 458/459/460/462 | Formatting toolbar |
| #xl-count | 464 | Row count display |
| #msg-input / #img-input / #img-btn / #send-btn | 471/472/473/474 | Input row |
| #img-preview-bar / #img-preview-thumb / #img-preview-name / #img-preview-cancel | 478/479/480/481 | Image preview |
| #chat-area / #empty-state | 497/498 | Message spreadsheet rows |
| #xl-status-user / #xl-collab / #xl-collab-name | 505/506/506 | Status bar |
| #clear-modal / #modal-cancel / #modal-confirm | 512/516/517 | Clear history modal |
| #call-history-modal / #call-history-close / #call-history-list | 531/535/537 | Call history modal |
| #call-history-clear-btn / #call-history-close2 | 541/542 | Call history modal buttons |
| #lock-overlay | 523 | Full-screen lock overlay |
| #img-lightbox / #img-lightbox-close / #img-lightbox-img | 548/549/550 | Image lightbox |
| #call-overlay | 554 | Full-screen call overlay |
| #remote-video / #local-video | 557/561 | WebRTC video elements |
| #call-status-panel / #call-cancel-wrap / #call-cancel-btn | 565/571/572 | Outgoing/status panel |
| #call-name / #call-status / #call-timer | 567/568/569 | Call info display |
| #incoming-panel / #incoming-name / #incoming-type | 578/580/581 | Incoming call panel |
| #call-reject-btn / #call-accept-btn | 584/588 | Incoming call buttons |
| #call-controls / #call-mute-btn / #call-cam-btn | 595/597/601 | Active call controls |
| #call-minimise-btn / #call-speaker-btn / #call-end-btn | 605/609/613 | Active call controls |
| #mini-call-bar / #mini-call-icon / #mini-call-name | 621/622/624 | Minimised call bar |
| #mini-call-timer-bar / #mini-call-maximise / #mini-call-end | 625/627/628 | Minimised call bar |

## index.html — JS State Variables (L633–L1414)
| Variable | L# | Purpose |
|---|---|---|
| authToken / myId / myUsername | 633/634/635 | Auth state |
| pollTimer / lastIncomingMsgId | 636/637 | Poll state |
| isMuted / isTyping / typingTimer | 638/640/639 | UI state |
| revealedMsgs | 641 | Decrypted message IDs |
| audioCtx | 645 | Web Audio context |
| pendingImage | 984 | Selected image before send |
| isLight | 1915 | Theme state |
| pc / localStream / callType / callState | 1401/1402/1403/1404 | WebRTC call state |
| callMinimised / micMuted / camOff | 1405/1406/1407 | Call UI state |
| pendingOffer / callPollTimer | 1408/1409 | Call signaling |
| callSeconds / callTimerInt / callStartEpoch / callStartedAt | 1410/1411/1412/1413 | Call timer |
| ringtoneTimer | 1414 | Ringtone interval |

## index.html — JS Functions
| Function | L# | Purpose |
|---|---|---|
| saveAuth / clearAuth | 702/708 | Auth token storage |
| api | 714 | Fetch wrapper with auth |
| login | 720 | Login handler |
| initApp | 739 | Post-login setup |
| updateStatus | 758 | Online/offline status |
| loadMessages | 790 | Fetch + render spreadsheet rows |
| revealRow / revealBubble | 942/688 | Decrypt message display |
| encryptText / escHtml / formatBody | 673/778/781 | Text helpers |
| sendMessage | 1064 | Send text/image |
| autoResize / setTyping | 1062/1094 | Input helpers |
| showTyping / hideTyping | 1099/1104 | Typing indicator |
| startPolling | 1107 | 1.5s poll loop |
| playNotification | 646 | New message sound |
| resizeAndEncode / showImgPreview / clearImgPreview | 988/1012/1019 | Image upload |
| openLightbox | 1056 | Full-screen image |
| applyFormat | 1123 | Bold/italic/underline |
| buildEmojiPicker | 1154 | Emoji grid |
| showLogin | 1326 | Navigate to login screen |
| pushSentinel | 1294 | Back-button history entry |
| showLock / hideLock / isLocked | 1245/1250/1254 | Lock overlay |
| _shieldRecents / _unshieldRecents | 1365/1373 | Recent tasks privacy |
| setAppHeight | 1343 | Mobile viewport fix |
| toggleTheme / applyTheme / applyThemeBtn | 1193/1917/1184 | Theme switching |
| toggleMute / updateMuteBtn | 1200/664 | Mute notifications |
| ICE_SERVERS (const) | 1388 | STUN/TURN config |
| createPC | 1531 | RTCPeerConnection factory |
| waitForICE | 1587 | ICE gathering wait |
| startCall / acceptCall / rejectCall / endCall | 1599/1645/1693/1699 | Call lifecycle |
| handleSignal | 1718 | Incoming signal router |
| sendSignal | 1419 | POST signal to server |
| startCallPoll / stopCallPoll | 1426/1438 | Signal polling |
| playRingtone / stopRingtone | 1443/1468 | Ringtone |
| startCallTimer / stopCallTimer | 1473/1487 | Call duration |
| showCallOverlay / hideCallOverlay | 1492/1505 | Call UI visibility |
| minimiseCall / maximiseCall | 1515/1523 | Minimize/restore call |
| logCall | 1825 | Log call to DB |
| openCallHistory / closeCallHistory / loadCallHistory | 1838/1842/1846 | Call history modal |
| formatDuration | 1882 | Seconds → M:SS |

## index.html — CSS Selectors (key ones)
| Selector | L# |
|---|---|
| #login-screen / .login-card / .login-logo | 89/103/108 |
| .shield-pulse / .shield-pulse2 | 111/112 |
| .login-title / .login-sub / .security-badges | 114/115/116 |
| .field-group / .btn-login | 118/127 |
| #lock-overlay / .lock-img-wrap | 142/147 |
| #app / .xl-ribbon / .xl-title | 163/185/191 |
| .xl-icon-btn / .xl-ribbon-btns | 193/194 |
| .xl-formula-bar / .xl-fx / .xl-cell-ref | 198/200/199 |
| .typing-indicator / .typing-dots | 205/207 |
| #chat-area / .xl-col-headers | 218/214 |
| .xl-row / .xl-row-num | 223/225 |
| .xl-cell-a / .xl-cell-b / .xl-cell-c / .xl-cell-d / .xl-cell-e | 227/229/235/335/336 |
| .xl-empty / .tick / .xl-lock | 239/236/237 |
| .xl-fmt-btn / .xl-fmt-sep / .xl-input-row | 245/247/250 |
| #msg-input / .xl-send-btn | 251/253 |
| .emoji-picker / .emoji-btn | 258/261 |
| .cell-img / #img-lightbox | 265/274 |
| .modal-overlay / .modal / .btn-cancel / .btn-confirm | 294/296/300/302 |
| .dropdown / .dropdown-menu | 306/307 |
| .hidden | 316 |
| .hamburger-menu / .hamburger-header / .hamburger-btn | 320/321/325 |
| .desktop-only | 329 |

## index.html — Event Listeners
| Element.event | L# |
|---|---|
| login-btn.click | 733 |
| send-btn.click | 1081 |
| msg-input.keydown / .input / .blur / .focus | 1137/1085/1348/1347 |
| theme-btn.click / mute-btn.click | 1211/1212 |
| header-clear-btn.click / menu-btn.click | 1213/1214 |
| hamburger-btn.click / hm-logout-btn.click | 1217/1221 |
| modal-confirm.click | 1237 |
| logout-btn.click | 1314 |
| img-btn.click / img-input.change / img-preview-cancel.click | 1026/1034/1046 |
| img-lightbox.click / img-lightbox-close.click | 1049/1052 |
| fmt-underline.click / fmt-emoji.click | 1136/1175 |
| call-history-btn.click / hm-call-history-btn.click | 1889/1890 |
| call-history-close.click / call-history-close2.click / call-history-clear-btn.click | 1894/1895/1896 |
| call-history-modal.click | 1900 |

## DB Schema
```
users:        id, username, password, token, online, last_seen, typing, last_active
messages:     id, sender_id, receiver_id, body, timestamp, status
signaling:    id, from_id, to_id, type, payload, created_at
call_history: id, caller_id, callee_id, call_type, status, started_at, duration
```
