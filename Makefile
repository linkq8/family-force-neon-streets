ifeq ($(strip $(PVSNESLIB_HOME)),)
$(error PVSNESLIB_HOME is required. Run ./tools/build.sh to use the pinned SDK)
endif

# Family Force: Street Rescue targets the broadest flash-cart baseline:
# standard chipless FastROM LoROM, 4 MiB, with no unused save RAM.
FASTROM := 1
HIROM := 0

export ROMNAME := family_force
export ROMTITLE := FAMILY FORCE RESCUE
export CARTRIDGETYPE := 00
export ROMSIZE := 0C
export SRAMSIZE := 00
export COUNTRY := 01
export LICENSEECODE := 00
export VERSION := 00
export ROMBANKS := 128

CFLAGS += -DSNES_TARGET

# The tracker module is converted to a PVSnesLib soundbank during the build.
AUDIOFILES := audio/stage_loop.it
export SOUNDBANK := audio/soundbank

include ${PVSNESLIB_HOME}/devkitsnes/snes_rules

.NOTPARALLEL:
.PHONY: all buildActual bitmaps brrsounds musics clean cleanProjectGfx

SMCONVFLAGS := -s -o $(SOUNDBANK) -V -b 5
BRRFILES := audio/punch.brr audio/jump.brr audio/damage.brr \
	audio/pickup.brr audio/confirm.brr audio/victory.brr

musics: $(SOUNDBANK).obj
brrsounds: $(BRRFILES)

all: cleanLogs buildWithSummary

buildActual: musics brrsounds bitmaps $(ROMNAME).sfc

clean: cleanBuildRes cleanRom cleanGfx cleanProjectGfx cleanAudio

cleanProjectGfx:
	@rm -f assets/dev/*.pic assets/dev/*.map assets/dev/*.pal \
		assets/dev/*.inc assets/dev/*_data.as

assets/dev/actors.pic: assets/dev/actors.png
	@echo "Converting 32x64 actor frames (two 32x32 OBJ halves)"
	$(GFXCONV) -s 32 -o 16 -u 16 -i $<

assets/dev/enemy_wave0.pic: assets/dev/enemy_wave0.png
	@echo Converting wave 1 static enemy pose pack
	$(GFXCONV) -s 32 -o 16 -u 16 -i $<

assets/dev/enemy_wave1.pic: assets/dev/enemy_wave1.png
	@echo Converting wave 2 static enemy pose pack
	$(GFXCONV) -s 32 -o 16 -u 16 -i $<

assets/dev/enemy_wave2.pic: assets/dev/enemy_wave2.png
	@echo Converting wave 3 static enemy pose pack
	$(GFXCONV) -s 32 -o 16 -u 16 -i $<

assets/dev/portraits.pic: assets/dev/portraits.png
	@echo Converting 64x64 character-select portraits
	$(GFXCONV) -s 64 -o 16 -u 16 -i $<

assets/dev/select_bg.pic: assets/dev/select_bg.png
	@echo Converting character-select background
	$(GFXCONV) -s 8 -o 16 -u 16 -p -m -y -i $<

assets/dev/street.pic: assets/dev/street.png
	@echo Converting scrolling street background
	$(GFXCONV) -s 8 -o 16 -u 16 -p -m -y -i $<

assets/dev/font.pic: assets/dev/font.png
	@echo Converting UI font
	$(GFXCONV) -s 8 -o 2 -u 16 -e 1 -i $<

bitmaps: assets/dev/actors.pic \
	assets/dev/enemy_wave0.pic \
	assets/dev/enemy_wave1.pic \
	assets/dev/enemy_wave2.pic \
	assets/dev/portraits.pic \
	assets/dev/select_bg.pic \
	assets/dev/street.pic \
	assets/dev/font.pic
