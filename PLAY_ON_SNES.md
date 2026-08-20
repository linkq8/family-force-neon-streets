# Playing on a real SNES

The release is a headerless, standard 4 MiB FastROM LoROM. It uses no Super FX,
SA-1, MSU-1, or other enhancement chip, so it fits the basic feature set of
common modern SNES SD-card flash cartridges. This alpha does not use save RAM
or create a game save.

## SD-card steps

1. Update the cartridge firmware/OS using its manufacturer's instructions.
2. Format the microSD card in the format required by the cartridge. FXPAK Pro
   explicitly requires FAT32 and does not support exFAT.
3. Copy `dist/family-force-street-rescue.sfc` into a games folder on the SD
   card. Do not put it inside the cartridge's firmware/system folder.
4. Eject the card safely from the computer and insert it into the flash cart.
5. With the SNES powered off, insert the cartridge and connect one or two
   standard controllers.
6. Power on, browse to `family-force-street-rescue.sfc`, and launch it.

The game detects 50 Hz PAL operation and adds simulation steps to preserve the
intended pace. Exact menu layout and SD formatting vary by cartridge. If it
does not launch, note the cartridge model, firmware version, SNES/Super Famicom
region, and whether other homebrew `.sfc` files work.

Manufacturer references:

- [FXPAK Pro product and SD requirements](https://krikzz.com/our-products/cartridges/fxpak-pro.html)
- [Super EverDrive X5 capabilities](https://krikzz.com/our-products/cartridges/spedx5.html)

Only use game files and cartridge hardware you are legally entitled to use.
