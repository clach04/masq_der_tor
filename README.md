# masq_der_tor

Server for Masq (2002) Shockwave PC game for defunct http://www.alteraction.com/


## What is Masq?

Shockwave (not flash).

  * https://www.igdb.com/games/masq
  * https://www.destructoid.com/indie-nation-30-masq/
  * https://web.archive.org/web/20100205171425/http://www.computerandvideogames.com/article.php?id=175128
  * https://lemmasoft.renai.us/forums/viewtopic.php?p=38481
  * https://lemmasoft.renai.us/forums/viewtopic.php?t=2815

## Where To Get It?

  * https://web.archive.org/web/20160606064916/http://www.alteraction.com/masq67.exe

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

  * http://www.alteraction.com/cgi-bin/
