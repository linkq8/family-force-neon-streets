-- Family Force: Street Rescue automated emulator smoke test.
--
-- Run with MesenCE's test runner:
--   Mesen --testRunner --timeout=20 tests/mesen_smoke.lua dist/<rom>.sfc
--
-- Controller input is injected from inputPolled, as recommended by Mesen's
-- Lua API.  The schedule enters the character-select screen, starts a one-
-- player game, walks into the stage, and exercises several combat buttons.

local frame = 0
local last_width = 0
local last_height = 0

local function validate_visible_frame(label)
    local pixels = emu.getScreenBuffer()
    local colors = {}
    local distinct = 0

    if pixels == nil or #pixels == 0 then
        emu.log("FAIL: " .. label .. " returned an empty screen buffer")
        emu.stop(1)
        return false
    end

    -- Sampling keeps the test quick while still rejecting a black/single-color
    -- boot, an uninitialized PPU, or a fully blank gameplay screen.
    for index = 1, #pixels, 97 do
        local pixel = pixels[index]
        if colors[pixel] == nil then
            colors[pixel] = true
            distinct = distinct + 1
        end
    end

    if distinct < 4 then
        emu.log(
            "FAIL: " .. label .. " has only " .. distinct ..
            " sampled screen colors"
        )
        emu.stop(1)
        return false
    end
    return true
end

local function button_is_down(first_frame, last_frame)
    return frame >= first_frame and frame <= last_frame
end

local function poll_controller()
    local pad = {
        a = false,
        b = false,
        x = false,
        y = false,
        l = false,
        r = false,
        up = false,
        down = false,
        left = false,
        right = false,
        select = false,
        start = false
    }

    -- Title -> character select, then character select -> gameplay.  Each
    -- press is separated by a long release window so edge-triggered menus see
    -- two unambiguous presses.
    pad.start = button_is_down(90, 93) or button_is_down(160, 163)

    -- Once gameplay has initialized, walk right and use every primary move.
    pad.right = button_is_down(220, 400)
    pad.down = button_is_down(250, 275)
    pad.up = button_is_down(310, 335)
    pad.y = button_is_down(260, 263) or button_is_down(345, 348)
    pad.x = button_is_down(290, 293) or button_is_down(380, 383)
    pad.b = button_is_down(325, 328)
    pad.a = button_is_down(415, 418)

    emu.setInput(pad, 0)
end

local function end_frame()
    frame = frame + 1

    if frame == 60 or frame == 200 or frame == 500 then
        local size = emu.getScreenSize()
        last_width = size.width
        last_height = size.height
        if last_width <= 0 or last_height <= 0 then
            emu.log("FAIL: emulator reported an invalid screen size")
            emu.stop(1)
            return
        end
        if not validate_visible_frame("frame " .. frame) then
            return
        end
    end

    if frame == 500 and io ~= nil then
        local output = io.open("/tmp/family-force-mesen-frame-500.png", "wb")
        if output ~= nil then
            output:write(emu.takeScreenshot())
            output:close()
        end
    end

    if frame >= 600 then
        local info = emu.getRomInfo()
        if info == nil or info.path == nil or info.path == "" then
            emu.log("FAIL: no active ROM was reported")
            emu.stop(1)
            return
        end

        emu.log(
            "PASS: booted ROM, entered gameplay, injected movement/combat, " ..
            "and completed 600 frames at " .. last_width .. "x" .. last_height
        )
        emu.stop(0)
    end
end

emu.addEventCallback(poll_controller, emu.eventType.inputPolled)
emu.addEventCallback(end_frame, emu.eventType.endFrame)
