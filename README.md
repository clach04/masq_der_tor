# masq_der_tor

Server for Masq (2002) Shockwave PC game for defunct http://www.alteraction.com/

## Current Status

Can start to play, (choose I do not want to register) but resuming (after not really starting the game) results in error:

    Director Player Error

    List expected for handler

    #append

This can be cleared by deleting the `Prefs` directory (contents).

    del Prefs\Xvl.txt Prefs\Xvlesp.txt Prefs\Xrecord.txt

## What is Masq?

Masq (2002) by https://www.crunchbase.com/person/javier-maldonado-c62b

Shockwave (not flash).

  * https://www.mobygames.com/game/28320/masq/
  * https://www.igdb.com/games/masq
  * http://alteraction-masq.blogspot.com/
  * https://www.destructoid.com/indie-nation-30-masq/
  * https://web.archive.org/web/20100205171425/http://www.computerandvideogames.com/article.php?id=175128
  * https://lemmasoft.renai.us/forums/viewtopic.php?p=38481
  * https://lemmasoft.renai.us/forums/viewtopic.php?t=2815

## Where To Get It?

  * https://web.archive.org/web/20160606064916/http://www.alteraction.com/masq67.exe
      * md5 checksum: 9770c6e29dd6cf2479943f3bb8491a61
      * size: 18,051,670 bytes

## Previous Work

https://github.com/KoleckOLP/masq_server

Main contributors; KoleckOLP, gamstat, and negativespinner

  * https://www.reddit.com/r/abandonware/comments/pv1djv/comment/jl86w1j/?utm_source=share&utm_medium=mweb3x&utm_name=mweb3xcss&utm_term=1&utm_content=share_button
  * https://www.reddit.com/r/abandonware/comments/pv1djv/comment/jjv8pjm/?force-legacy-sct=1
  * https://www.reddit.com/r/abandonware/comments/pv1djv/comment/jkflp4r/?force-legacy-sct=1

## Related

  * https://github.com/ProjectorRays/ProjectorRays - Decompiler for Macromedia Shockwave/Macromedia Director/Adobe Shockwave/Adobe Director

## Reverse Engineering Notes

  * `strings` on the Windows binary doesn't reveal anything useful (presumbly compressed resources, see decompiler note)
  * KoleckOLP ran through decompiler
  * Most end points determined through reverse engineering the code and REST calls by KoleckOLP and gamstat

URL endpoints are all over http (not https):

  * http://alteraction.com/cgi-bin/
      * NOTE **not** www.alteraction.com
      * domain name "alteraction.com" is 15 bytes. E.g. "http://123456789012345/cgi-bin/"
      * could potentially have 21 byte domain with modified url of /x/. E.g. "http://123456789012345678901/x/"
      * shorter is possible, as long as memory in client binary is zero'd out with NUL

After connecting the client displays a license agreement screen with:

  * messagetext.cost
  * messagetext.more
  * messagetext.license

Online help URL is http://www.alteraction.com/auxiliars/help.htm (45 bytes).

### Client Binary

Stores preferences, config, and progress/decisions in a local directory `Prefs` to the `masq67.exe`:

    Xrecord.txt - starts zero length on game start. Might be list of answers in play through?
    Xrecord2.txt - ony appears after (second) completion? Might be list of answers in play through?
    Xvl.txt - game state?
    Xvlesp.txt - game state?
    XAlterid.txt  - user name and password


### Network

Either update your DNS server to redirect or local hosts file.
Alternatively see https://github.com/KoleckOLP/masq_server for in-memory patch of server URL, see https://github.com/KoleckOLP/masq_server/pull/2

    /etc/hosts
    %windir%\System32\drivers\etc\hosts
    Often `C:\WINDOWS\System32\drivers\etc\hosts`.

Add to end:

    127.0.0.1   alteraction.com

Optionally add www.alteraction.com to avoid domain squatter issue when clicking help.
