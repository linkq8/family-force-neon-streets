.include "hdr.asm"

.section ".actors_tiles" superfree

; Exactly one 32 KiB LoROM bank. Keep palettes and other data elsewhere.
actors_til:
.incbin "assets/dev/actors.pic"
actors_tilend:

.ends

.section ".enemy_wave0_tiles" superfree

enemy_wave0_til:
.incbin "assets/dev/enemy_wave0.pic"
enemy_wave0_tilend:

.ends

.section ".enemy_wave1_tiles" superfree

enemy_wave1_til:
.incbin "assets/dev/enemy_wave1.pic"
enemy_wave1_tilend:

.ends

.section ".enemy_wave2_tiles" superfree

enemy_wave2_til:
.incbin "assets/dev/enemy_wave2.pic"
enemy_wave2_tilend:

.ends

.section ".portrait_tiles" superfree

portraits_til:
.incbin "assets/dev/portraits.pic"
portraits_tilend:

.ends

.section ".actor_palettes" superfree

actors_pal:
.incbin "assets/dev/actors.pal"
actors_palend:

enemy_wave0_pal:
.incbin "assets/dev/enemy_wave0.pal"
enemy_wave0_palend:

enemy_wave1_pal:
.incbin "assets/dev/enemy_wave1.pal"
enemy_wave1_palend:

enemy_wave2_pal:
.incbin "assets/dev/enemy_wave2.pal"
enemy_wave2_palend:

portraits_pal:
.incbin "assets/dev/portraits.pal"
portraits_palend:

.ends

.section ".font_data" superfree

.include "assets/dev/font_data.as"

.ends

.section ".street_data" superfree

.include "assets/dev/street_data.as"

.ends

.section ".select_bg_data" superfree

.include "assets/dev/select_bg_data.as"

.ends

.section ".sound_effect_data" superfree

sfx_punch:
.incbin "audio/punch.brr"
sfx_punch_end:

sfx_jump:
.incbin "audio/jump.brr"
sfx_jump_end:

sfx_damage:
.incbin "audio/damage.brr"
sfx_damage_end:

sfx_pickup:
.incbin "audio/pickup.brr"
sfx_pickup_end:

sfx_confirm:
.incbin "audio/confirm.brr"
sfx_confirm_end:

sfx_victory:
.incbin "audio/victory.brr"
sfx_victory_end:

.ends
