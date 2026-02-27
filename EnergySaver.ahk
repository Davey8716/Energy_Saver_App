#Requires AutoHotkey v2.0

SetKeyDelay(50, 50)   ; improves reliability on Win11

; -------------------------------
; Open Quick Settings
; -------------------------------
Send("#a")

; Wait for panel instead of guessing timing
WinWaitActive("Quick Settings", , 2)

; -------------------------------
; Focus tile grid
; -------------------------------
Send("{Tab}")


; -------------------------------
; Navigate directly to Energy Saver
; -------------------------------
Send("{Down 3}")


Send("{Space}")   ; toggle


; -------------------------------
; Close Quick Settings
; -------------------------------
Send("#a")

ExitApp

