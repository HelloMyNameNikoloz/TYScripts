#Requires AutoHotkey v2
#SingleInstance Force

; ─── SPEED TWEAKS ───────────────────────────
SendMode("Input")        ; fastest mode
SetKeyDelay(-1, -1)      ; no inter-key delay
; ────────────────────────────────────────────

; ─── CONFIG ─────────────────────────────────
frames   := 15           ; always jump 15 frames
interval := 500          ; ms between cycles (0.5 s)
; ────────────────────────────────────────────

toggled := false
step    := 0             ; 0→move+cut, 1→move+cut, 2→back+delete

F6:: {
    global toggled, step, interval
    toggled := !toggled
    if toggled {
        step := 0
        SetTimer(DoCut, interval)
    } else {
        SetTimer(DoCut, 0)
    }
}

DoCut(*) {
    global frames, step

    if (step < 2) {
        ; step 0 & 1: move 15 frames + cut
        SendInput("{Right " frames "}")
        SendInput("^+k")
    } else {
        ; step 2: back 1 frame + select + delete
        SendInput("{Left}")
        SendInput("d")
        SendInput("+{Del}")
    }

    ; advance step: 0→1→2→0→…
    step := Mod(step + 1, 3)
}
