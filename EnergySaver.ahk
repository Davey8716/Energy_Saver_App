#Requires AutoHotkey v2.0

SetKeyDelay(50, 50)

eco := A_Args.Length >= 1 ? A_Args[1] : ""

if (eco = "")
    ExitApp

Send("#a")
WinWaitActive("Quick Settings", , 2)

Send("{Tab}")
Send("{Down 3}")
Send("{Space}")

Send("#a")
ExitApp