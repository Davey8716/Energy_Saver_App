#Requires AutoHotkey v2.0

SendMode("Input")
SetKeyDelay(0, 0)

eco := A_Args.Length >= 1 ? A_Args[1] : ""

if (eco = "")
    ExitApp(1)

Send("#a")

; On this Windows build Quick Settings does not provide a stable window title
; for WinWaitActive.  Give its controls time to initialise after sign-in before
; sending the existing keyboard navigation.
Sleep(3000)

Send("{Tab}")
Send("{Down 3}")
Send("{Space}")

; Allow the selected tile to receive the action before hiding Quick Settings.
Sleep(500)
Send("#a")
ExitApp(0)
