# Get ANY OFFICIAL badges without other user's data

## Introduction

This thread will guide you through on how to get any official badge you could possibly think of, and also how to group each badge into sets.

**NOTE**: Nintendo's servers have officially "shutdown" as of the 8/4/2024 and the downloading part of Allbadge Tool may stop working any day since it still relies on said servers. Replacing the links with mirrors that lead to the same files could be a way to go, but until the servers are fully down, we'll have to wait.

## Setup

Before starting, you're going to need a few things:

- [A modded 3DS with boot9strap](https://3ds.hacks.guide/)
- [Simple Badge Injector](https://github.com/AntiMach/simple-badge-injector/releases/latest)
- [Allbadge Tool](https://github.com/AntiMach/allbadge-tool/releases/latest)
- [Advanced Badge Editor](https://github.com/AntiMach/advanced-badge-editor/releases/latest)
- A way to read your SD card

## Assumptions

This guide assumes the following:

- You followed the [3ds.hacks.guide](https://3ds.hacks.guide/) step by step to mod your 3ds, or update your modded 3ds.
- You know some basic understanding of transferring files from your 3DS's SD card to your PC and vice versa.

## Getting the arm9 bootrom

This will be needed for the allbadge tool, as it is required for decrypting some files.

- Boot your 3DS holding `Start`. This should open **GodMode9**
- Move to `[M:] MEMORY VIRTUAL` and press `A`
- Move to `boot9.bin` and press `A`
- Move to `Copy to 0:/gm9/out` and press `A`
- While holding `R`, press `Start` to turn your 3DS off

Your `boot9.bin` file should now be on your SD card inside of `/gm9/out`.

## Getting the badges

Having obtained the arm9 bootrom, you can now use the **Allbadge Tool**.

- Make sure your `boot9.bin` is in the same folder as `allbadge_tool.exe`
- Open `allbadge_tool.exe`
- Select the versions you wish to download `ex.: EUR v131`
- Click the begin button
    - Wait until everything is done
    - If any error occurs, make sure to read what the error says. If it's something you can solve manually, do it so. Report any other weird errors to me
- Once done, you should have zip files for the badges you want inside a `data` folder
- You may want to extract the folders for the sets you want

With this step done, we now have all the badges.

<details>
  <summary><b>EXTRA: Getting badge data from the Nintendo Badge Arcade updates</b></summary>

  This is not usually needed, but may include badges that are otherwise missing on the other files.
  
  - Move [this GodMode9 script](https://github.com/AntiMach/allbadge-tool/releases/tag/gm9script) to the `/gm9/scripts` folder on your SD card
  - Boot your 3DS holding `Start`. This should open **GodMode9**
  - Press the `HOME` button
  - Nagivate to `Scripts...` > `BadgeExtractTool`
  - Select the desired options from here
  - Select `Exit` and press `A` once you're done
  - While holding `R`, press `Start` to turn your 3DS off
  - Take any `pc_REGION.sarc` file from the `/gm9/out` folder on your SD card and move them to the `data` folder of the **Allbadge Tool**
  - Running the **Allbadge Tool**, you can now make use of the `pc REGION` options to extract their contents

  With this step done, we now have ALL the badges (specially if you extracted the Japanese sarc).
</details>

## Creating badge data

To actually import the extracted badges, you will need to use **Advanced Badge Editor**.

- Open `Advanced_badge_editor.exe`
- Go to `File` > `New data`
- Go to `Import` > `Entire set data (*.prb and *.cab)`
    - An alternative to this process could involve using the **Simple Badge Injector** to dump your own `BadgeData.dat` and `BadgeMngFile.dat` files
    - In that case, use `File` > `Open data` and select the folder where those files are
- Select the set's `.cab` file
- Select the set's `.prb` files (you can select multiple)
- Click `255 of each badge` for essentially all the badges you need
- Go to `File` > `Save data to...`
- Select a folder to save the badge files to
- You can close the app

Now you should now have seemling legit `BadgeData.dat` and `BadgeMngFile.dat` files.

## Installing Simple Badge Injector and injecting the data

Finally, to use your badges, you're going to need to inject them.

- Move the `SimpleBadgeInjector.cia` to anywhere on your SD card
- Move the `BadgeData.dat` and `BadgeMngFile.dat` files to `/3ds/SimpleBadgeInjector` relative to the SD card's root
    - If the folder doesn't exist, make sure to create it and name it exactly the same!
- Boot your 3DS with the SD card inside
- Open `FBI`
- Install the `SimpleBadgeInjector.cia`
- Close `FBI`
- Open `Simple Badge Injector`
- Select `Dump badge data`. This will backup any badge data you might have *(optional)*
- Select `Inject badge data` and press `A`
    - In case any errors occur, please report them to me
- Return to the home menu

You should now have access to a generous amount of official badges!

## Credits

This guide would not have been possible without a lot of research done by other people:
- [3DBrew](https://www.3dbrew.org/) for documenting most of data I had to deal with
- [Custom Mario Kart Wiki](https://wiki.tockdom.com/) for having information on Yaz0 compressed files
- [SciresM's BadgeArcadeTool](https://github.com/SciresM/BadgeArcadeTool) for code on reading and extracting `SARC` archives
- [yellows8's boot9_tools](https://github.com/yellows8/boot9_tools) for having a lot of information on the ARM9 Bootrom's AES keys

Please report any issues on the respective Gbatemp thread, or on this repository!





