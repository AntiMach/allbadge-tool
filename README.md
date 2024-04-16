# Obtaining Official Badge Data

## Requirements

- `boot9.bin`, the FIRM9 bootrom
    - preferably not from a dev unit
- some disk space (at most 1GB)
- internet connection

## Process

### 1. Dump the boot9.bin

This step must be done manually, and can be done via GodMode9.
The file is in `MEMORY VIRTUAL`.

### 2. Obtain the BOSS decryption key

This key is in the bootrom, and will be used to decrypt the downloaded data.

The exact location:
- Skip `0x8000` bytes (first half of the bootrom)
- Skip `0x5860` bytes (reach keyarea)
- Skip `0x170` bytes (skip AESIV data that's not necessary here)
- Skip `0x200` bytes (skip to the BOSS decryption key, keyslot 0x38) 
- Read `0x10` bytes (the key has 128 bits)

In other words, the BOSS encryption/decryption key is at `0xDBD0`, with size of `0x10` bytes.

### 3. Download the badge data

The files can be obtained through the following link:

`https://npdl.cdn.nintendowifi.net/p01/nsa/{REGION_CODE}/data/allbadge_v{VERSION}.dat?tm=2`

Changing `REGION_CODE` with any of the following values:

- JPN: `j0ITmVqVgfUxe0O9`
- EUR: `J6la9Kj8iqTvAPOq`
- USA: `OvbmGLZ9senvgV3K`

And the `VERSION` with either `130` or `131`

The files are [BOSS encrypted containers](https://www.3dbrew.org/wiki/SpotPass#Content_Container).

### 4. Decrypting the badge data

The BOSS containers are encrypted using AES encryption in CTR mode.

The key used is the one obtained from the bootrom.

The initial value is in the header of the BOSS container, and is unique to each container.

The process is as follows:
- Obtain the first 12 bytes of the initial value from the bytes `[0x1C,0x28[` in the file.
- The last 4 bytes are an unsigned integer with value 0x1, big endian. (`0x00 0x00 0x00 0x01`).
- Run the AES-CTR algorithm on the file starting at `0x28`.
- Trim the first `0x26E` bytes of the decrypted file (or `0x296` bytes if you count the BOSS header), as those are BOSS container files.

The decrypted file is then revealed to be a SARC archive.

### 5. Extracting the badge data

Yeah, this one I am NOT explaining, the code is in allbadge_tool.ctr.sarc.

### 6. Repackage the badge data

For comodity's sake, the files are organized by their badge and set names in a zip archive, as that is all that is needed.

### An alternative to storage

Store every file based on their hash, and point to their data in a database, for ease of access.

### Result

From a single `boot9.bin` to zip archives, this process obtains official `.prb` and `.cab` files, badges and collections respectively.


# Building the executable (Windows)

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller executable.py --noconsole
```