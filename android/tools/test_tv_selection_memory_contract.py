#!/usr/bin/env python3
"""Guard the TV character picker against synchronous atlas decoding."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java"


def method_body(text: str, signature: str, next_signature: str) -> str:
    start = text.index(signature)
    end = text.index(next_signature, start)
    return text[start:end]


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    select = method_body(text, "private void beginCharacterSelect()", "private void resetInputsForSelectFailure()")
    navigate = method_body(text, "private void navigateMenu(", "private float attackReach(")
    select_slot = method_body(text, "private void selectHeroForActiveSlot(", "private void toggleSelectionSlotAfterConfirm()")
    move_cursor = method_body(text, "private void moveMenuCursor(", "private void applyDirectionalActionForMenu(")

    assert "unloadSelectedHeroAnimation();" in select
    assert "unloadPlayer2Animation(false);" in select
    for body in (select, navigate, select_slot, move_cursor):
        assert "loadSelectedHeroAnimations();" not in body
        assert "loadPlayer2Animations();" not in body

    start = method_body(text, "private boolean tryConfirmSelectionToStart()", "private void beginCharacterSelect()")
    assert "loadSelectedHeroAnimations();" in start
    assert "if (twoPlayerMode) loadPlayer2Animations();" in start
    print("TV selection memory contract: PASS")


if __name__ == "__main__":
    main()
