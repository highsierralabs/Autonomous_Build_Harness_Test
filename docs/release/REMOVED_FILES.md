# Removed files

This repository was built from a filtered clone of a private working
repository. Forty-eight PNG probe captures were removed from **every commit**
of that history, not merely from the tip. They are listed here in full so the
absence is declared rather than silent.

## Why

Each removed capture is a full-page browser screenshot taken while the probe
ran against the live RHACO corpus, and several render the complete body of a
governed RHACO document as a bitmap that no text scan of this repository could
inspect. Because the original history contained no deletions at all, removing
them at the tip alone would have left every one of them reachable from an
earlier commit.

## What was kept

The structured JSON observations produced by the same probe runs are retained.
They record what each run measured -- verdicts, timings, HTTP status, fault
classes, qualification state -- without reproducing document bodies as images.
Twenty-nine fixture-backed captures are also retained; every one of them was
viewed before release, and each renders either a synthetic fixture document, a
fixture-index diagnostics page, or an error body.

## The removed files

48 files, 26746059 bytes (25.5 MB). SHA-256 is of the file content; the blob id is
the git object id the path held at the original tip.

| Path | Bytes | SHA-256 | Blob |
|---|---|---|---|
| `docs/probe-qualification/runs/20260904T034711Z/diagnostics.png` | 345131 | `571e14004fbb0341e22d2f5cc26c804d61d203e67becd44adbff369c0f839032` | `42d0570089fb3dc8f212edf68ac7f8ba306f2a52` |
| `docs/probe-qualification/runs/20260905T002845Z/diagnostics.png` | 468999 | `caf004458affa05082a645abfab14ba0745a3b713b784b647cb62fc9b77490c6` | `c311266cb4dc3c62e6f7cba1120936dfde42a415` |
| `docs/probe-qualification/runs/20260905T014316Z/W1.png` | 1093356 | `639fd840154e8ad5f6a45752884470db3779ecbb7b2165333f58159e2052e828` | `1487a22c761fdf8164e736a3c9237b31aa025ac3` |
| `docs/probe-qualification/runs/20260905T014319Z/W2.png` | 580345 | `f69e2f6d437fca6076ec59340f7acee45ef02b64ebba89ca7bd6e4957e27dd3a` | `ad75a896bfb6dcfc85781be8a23706f06fb6c0b4` |
| `docs/probe-qualification/runs/20260905T014330Z/W3.png` | 226559 | `3d533c7fad395a284439150a2116e8544948cf9cb130d2bc45edcafa541d308c` | `a21b4c9b1e0ade2fb415f67b7cc9ec4995421406` |
| `docs/probe-qualification/runs/20260905T014336Z/W4.png` | 442877 | `eadf1ec8e32bc03443ecff4466094ebc2f4eec07421cb72c9f834c77077ab4d8` | `c8f1bc00c1c98bebab3e5ee3c30717d89dcf2faa` |
| `docs/probe-qualification/runs/20260905T014346Z/W9.png` | 1293139 | `edd9c7c436430525360fb8e770ac81df7b0da2e582353e698de49c636bdabb4c` | `03baaffd8b09e98ca75a3c7b68a842308fdca5e8` |
| `docs/probe-qualification/runs/20260905T014349Z/W10.png` | 266386 | `949521ae6a15baae2bc0fb2c8b49617dd9320ac2bb8c09dbeca3970d6f1a3798` | `2253a7619dda33560cd631e74713801d0e5cee8f` |
| `docs/probe-qualification/runs/20260905T014402Z/diagnostics.png` | 266837 | `311966fe7931e004472085810be798f726e2b2f2bc8ecb473af82642bd2ecca5` | `9fcd339ed7e6e5dce8e9c82a48fc7156b20b5dfc` |
| `docs/probe-qualification/runs/20260905T014404Z/W7.png` | 276997 | `c6c094dbfc615729904a3109c12148f5f42355b9dd3b40123ed49c02efb120fe` | `7c47aaf6f5e829050906849c533343b07995af54` |
| `docs/probe-qualification/runs/20260905T020025Z/W1.png` | 1093356 | `639fd840154e8ad5f6a45752884470db3779ecbb7b2165333f58159e2052e828` | `1487a22c761fdf8164e736a3c9237b31aa025ac3` |
| `docs/probe-qualification/runs/20260905T020028Z/W9.png` | 1293139 | `edd9c7c436430525360fb8e770ac81df7b0da2e582353e698de49c636bdabb4c` | `03baaffd8b09e98ca75a3c7b68a842308fdca5e8` |
| `docs/probe-qualification/runs/20260905T020032Z/W10.png` | 265339 | `77b9b5457cc08f2a35f5d58ec901b6a40f241874b64fc3a646a17c18be44973a` | `0525ace99858d48bd0e336e16a00f3bc5588eca5` |
| `docs/probe-qualification/runs/20260905T020036Z/W7.png` | 274900 | `5c831750e5bce415289133529766f2e9b322f711199393a59c737bbc77aed1d1` | `48a25fcf578fa393b4aab41436ea89b79b5f5b36` |
| `docs/probe-qualification/runs/20260905T043130Z/W1.png` | 1107576 | `c58f057dd00e8501afc46b0b7df3bd970364ad3f0f311bdfc18aff1d0ab1c9f4` | `6a30ad088a988e69ec1b85500286bc86da1ef771` |
| `docs/probe-qualification/runs/20260905T043133Z/W2.png` | 650677 | `8661836138f3ceb2e420aa453f689d16d6eff4dd9509d342d007daf720b85f45` | `1772e24457a0ab3f52ab24b38152653779a3ce83` |
| `docs/probe-qualification/runs/20260905T043136Z/W3.png` | 266579 | `9e217891002b9c39cad21387b91a63803f7df160989dd967c6299940055c59ff` | `5f24ae14d48ea154d1e1920abb2f00596e41d2db` |
| `docs/probe-qualification/runs/20260905T043142Z/W4.png` | 441746 | `a8856e62c3cf5fb9a1fd7f1fe58c67ff9d7653c5cfcdb69f1e1cb0b59484e32c` | `1de20b139bf89c1a07bd533b86402dea265d612d` |
| `docs/probe-qualification/runs/20260905T043145Z/W5.png` | 400149 | `63b483b45c0c2b795c37e5a93714cdf92d7e5f0d9f9548c4c5e9d9213907b5be` | `d63fe8b77ea4595730234f86622d1e1ccce53cc5` |
| `docs/probe-qualification/runs/20260905T043147Z/W6.png` | 465244 | `912ceeadcf3784fa1fa12ad3c30d1a67f2c42bd350ab65a1ccc000e8c94e6fd6` | `96ef5f36e2fa8f85b782f6e9c3844e032fef16d5` |
| `docs/probe-qualification/runs/20260905T043150Z/W8.png` | 294254 | `c204bbd160ab5af55491939e3e0bd6cbd57862aad996ce2bd9974a3458faf005` | `0ac068b91ce0da3b0a088855abb59d3951b6a97b` |
| `docs/probe-qualification/runs/20260905T043154Z/W9.png` | 1304519 | `53713747234b0a361a149008eb0995441155e016c3af3ee03327a09b383af65d` | `9eecd51198a2463ca4787950b9f3f3f17c82bd20` |
| `docs/probe-qualification/runs/20260905T043157Z/W10.png` | 279405 | `d8ab4af3b9ee950abc343271a4797febe1d7f4fb18fad4f81fcd469a8435ea63` | `120ee4915d54be7bf73df0a48f4d366c5009eca1` |
| `docs/probe-qualification/runs/20260905T043203Z/diagnostics.png` | 279754 | `856e0bd619ac0a0f32c37c381f634ea569404d1db4233913c546f54c02f1aa41` | `2829e8d5f032515c36363bad1e4e5138e6b4520c` |
| `docs/probe-qualification/runs/20260905T043213Z/W7.png` | 289889 | `2cd2f5dbc461c0893f2b10db09c7365a4c574e8002f466dc97f70934f2205d23` | `c20faa0010f70b0c92e2665a330789773fa43f73` |
| `docs/probe-qualification/runs/20260905T050330Z/W6.png` | 465244 | `912ceeadcf3784fa1fa12ad3c30d1a67f2c42bd350ab65a1ccc000e8c94e6fd6` | `96ef5f36e2fa8f85b782f6e9c3844e032fef16d5` |
| `docs/probe-qualification/runs/20260905T050346Z/W1.png` | 1107576 | `c58f057dd00e8501afc46b0b7df3bd970364ad3f0f311bdfc18aff1d0ab1c9f4` | `6a30ad088a988e69ec1b85500286bc86da1ef771` |
| `docs/probe-qualification/runs/20260905T050349Z/W2.png` | 650677 | `8661836138f3ceb2e420aa453f689d16d6eff4dd9509d342d007daf720b85f45` | `1772e24457a0ab3f52ab24b38152653779a3ce83` |
| `docs/probe-qualification/runs/20260905T050353Z/W3.png` | 266579 | `9e217891002b9c39cad21387b91a63803f7df160989dd967c6299940055c59ff` | `5f24ae14d48ea154d1e1920abb2f00596e41d2db` |
| `docs/probe-qualification/runs/20260905T050359Z/W4.png` | 441746 | `a8856e62c3cf5fb9a1fd7f1fe58c67ff9d7653c5cfcdb69f1e1cb0b59484e32c` | `1de20b139bf89c1a07bd533b86402dea265d612d` |
| `docs/probe-qualification/runs/20260905T050401Z/W5.png` | 400149 | `63b483b45c0c2b795c37e5a93714cdf92d7e5f0d9f9548c4c5e9d9213907b5be` | `d63fe8b77ea4595730234f86622d1e1ccce53cc5` |
| `docs/probe-qualification/runs/20260905T050404Z/W8.png` | 277313 | `f053b0a7178610a53ea629343218c47d8dcfc614bdd0324dcb8d1ab5eaf2d366` | `3474f3125b1c642979a3b5bd0a4b4290f0525b46` |
| `docs/probe-qualification/runs/20260905T050408Z/W9.png` | 1304519 | `53713747234b0a361a149008eb0995441155e016c3af3ee03327a09b383af65d` | `9eecd51198a2463ca4787950b9f3f3f17c82bd20` |
| `docs/probe-qualification/runs/20260905T050411Z/W10.png` | 277665 | `41c513e1163cbc1a1e15ee6fc36c13a0dbc72d981c2c9c9fc378ec5eb75bec72` | `2f43028513dc6830d72d5d8bb7952822439c8cec` |
| `docs/probe-qualification/runs/20260905T050417Z/diagnostics.png` | 277862 | `2370b83874c7506b5575ec35f645ddcdb2d368bd069a312fe21c97d95d3df63f` | `5c5ed5b3bd98b67419299c4313ccdf94fecab7d7` |
| `docs/probe-qualification/runs/20260905T050419Z/W7.png` | 288018 | `7eb83100c4193a9c80ea5451da6df3f727b203a88bdaf1d3494407606a9cf46c` | `6c3ccb2df1f70dde391752c0c11c275e5fb667bb` |
| `docs/probe-qualification/runs/20260905T164214Z/W4.png` | 759830 | `df4b619669dd31136bf0941f33d4be3ef83d43c4a64cc1303e6926198a8aaaa6` | `e8686969f8672cdcd90714144f42b836c74733a9` |
| `docs/probe-qualification/runs/20260905T171444Z/W1.png` | 1126064 | `243aeba29fbc87fb6858a9e5b4ab7fe7564a95fea0e124f55c5440457c7e43d8` | `70ac1e764eae9c33bd829954f15f9d5b4013b237` |
| `docs/probe-qualification/runs/20260905T171447Z/W2.png` | 666876 | `cc2c2c8a65a50a77acf76f48516ee52659899b76df792134d38dc77f1500aaef` | `e1d41e8133abe9513eb2f133859236089c147751` |
| `docs/probe-qualification/runs/20260905T171451Z/W3.png` | 282664 | `c8006009cf89eadb8f52076a353ce1d9f365954f054578fd452b6ed46186b7a9` | `8218abffa043fd00a4cb4ae0a713d2eb3b1157fb` |
| `docs/probe-qualification/runs/20260905T171457Z/W4.png` | 760784 | `a8b2b2a523de73818a931e565ca420587e74b3f5cc7e1be6de2d2ab95d57694d` | `86d410a275deaa265d3c08c62506d368ec996658` |
| `docs/probe-qualification/runs/20260905T171500Z/W5.png` | 470093 | `9c1bb5ca4a025ba0f0f147f9225170b6316bb9d98f24d17e77649c4826a6d91d` | `23c2a9bc9bdf946865479da0c95755b88fab7bbe` |
| `docs/probe-qualification/runs/20260905T171503Z/W6.png` | 513142 | `f29a8fc9002d3d00729d44be76f75a060f788fa2b626898e2f23a92d76186061` | `4a92b6f769a2d33474aaff40096f731d31712883` |
| `docs/probe-qualification/runs/20260905T171506Z/W8.png` | 277578 | `93f3d35cb13e658019d780892eca2d5655b0dedc13151baed6c925908ade1705` | `28e743b3daf7c31442dcbd0f6a54f79cf395efea` |
| `docs/probe-qualification/runs/20260905T171510Z/W9.png` | 1319869 | `0ac6b6e0e697c5e48ac2fd178983080baaca2399a461555749e5710e890f80f8` | `cbe0ab40c0e3711d19efd9671ae16cc14d90b211` |
| `docs/probe-qualification/runs/20260905T171514Z/W10.png` | 277765 | `491daf99741665ea92e4abe0f3f566a133c85c848cb69125137594075849a53a` | `757413a82fe5150d5bb7a1e8709366a713b2e6df` |
| `docs/probe-qualification/runs/20260905T171520Z/diagnostics.png` | 278372 | `1074028ee5df0e3e0573636f0bb817893dfa9faf8e896fb8986b0cebf6397d66` | `c6f2d19e928650161b350ab894f9935344b25ec1` |
| `docs/probe-qualification/runs/20260905T171534Z/W7.png` | 288522 | `7c775d3265ad9eb565a9fd87edb92859710ddec98ba35fe17f795c28648b7b22` | `86839e448d41c13e12d875296a9b79b76ed9ce9a` |

Forty-eight paths resolve to 39 distinct blob ids, because some captures are
byte-identical to another. Every one of those blob ids was confirmed absent
from the object store after the rewrite, following reflog expiry and garbage
collection.

## Translating commit ids

Rewriting history changes every commit id from the point of the first change
onward. Build records inside this repository cite commit ids from the original
repository and were deliberately left as written. `commit-map.txt` in this
directory maps each original id to its rewritten one.
