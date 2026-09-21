# Campaign snapshot -- manifest

**These are unedited, non-canonical copies.** Each file below was copied byte
for byte out of the private RHACO repository at commit `8f79960` and is
reproduced here so the campaign that produced this build can be read alongside
it. Nothing was normalised, reflowed, or relinked. **The RHACO repository
remains the record of authority**; where a copy here and the RHACO original
ever differ, the original governs.

Snapshot commit: `8f79960`

## Dangling identifiers

These copies cite RHACO documents by identifier. Most of those documents are
not part of this snapshot, so the identifier resolves to nothing here -- that
is what a *dangling* identifier means below. It is not an error and not a
broken link; it is the expected consequence of copying a subset of a governed
corpus. The identifier still names a real document in the RHACO repository.

- identifiers provided by this snapshot: **12**
- distinct identifiers cited: **44**
- distinct identifiers that dangle: **32** (129 citations in total)

## Cards are not included

Every governed RHACO document has a sibling `.card.yaml` carrying its catalog
metadata. No card is copied here. The documents appear without them.

## Verifying a copy

The SHA-256 values below are of the bytes stored in this repository. The
repository sets `* -text` in `.gitattributes`, which turns off end-of-line
conversion, so a checkout on any platform reproduces those bytes and the
hashes can be checked directly against the working tree.

## Errata

| File | Erratum |
|---|---|
| `RHACO_Build_Prompt_Template_v2_0.md` | Its provenance paragraph states that the upstream file as retrieved was retained in RHACO working material. The named file is RHACO's own v0 generalisation, and no copy of the upstream was kept. Corrected in v2.2 by RHACO-CHG-20260920-001. |
| `RHACO_Build_Prompt_Template_v2_1.md` | Same statement, carried forward from v2.0. Corrected in v2.2 by RHACO-CHG-20260920-001. |

Both versions are reproduced as written. The correction is recorded here
rather than applied to them, because these are historical copies.

## Files

`Tracked` records whether the source was tracked in the RHACO repository at
snapshot time. Three files were not: the builder's handback and the two
pre-governance prompt drafts under `unfiled/`.

| File | Source in RHACO | Bytes | SHA-256 | Blob | Tracked |
|---|---|---|---|---|---|
| `HND-20260903-001_report.md` | `working\HND-20260903-001_report.md` | 196366 | `790796903b952994c5f83f2e3dbc499c873dfa96a1a222cd07577ea0a414d4a2` | `241869dea2e0` | untracked at snapshot time |
| `RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md` | `docs\reports\RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation.md` | 31386 | `c6b6421c5734e797de1f01476f15b61c90f40569c1dd4d95548dde5f58c04b03` | `7fa46990855a` | yes |
| `RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation_Amendment_A1_Gate_Caught_Class_B_Instance.md` | `docs\reports\RHACO-ANL-20260905-001_Corpus_Explorer_Harness_Evaluation_Amendment_A1_Gate_Caught_Class_B_Instance.md` | 4218 | `1dcd86fb96d074214f9a56be4e895fb9cf32445928bf553fd9d5c370a7678954` | `afae95c95aae` | yes |
| `RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md` | `docs\reports\RHACO-ANL-20260907-001_Build_Prompt_Template_Review.md` | 23462 | `09bb5408d85ee649ccfd5502c4eb4bbf45c1ae1b071b8a8c84440d5469305265` | `7205cbaef49f` | yes |
| `RHACO-ANL-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep.md` | `docs\reports\RHACO-ANL-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep.md` | 31319 | `bcf84a3c5d2e48988b094dee7f15a40f8dbeb208e29a5777541a8e13acf03b95` | `aead638f291f` | yes |
| `RHACO-CCX-20260904-001_Corpus_Explorer_Build_Shepherd_Handoff.md` | `docs\reports\RHACO-CCX-20260904-001_Corpus_Explorer_Build_Shepherd_Handoff.md` | 17976 | `b1dc66eb216084af66d1566c6dd434b3b0f384e8ac0d7dca05450486fd7f6a2e` | `03ee9674e8d4` | yes |
| `RHACO-CCX-20260905-001_Corpus_Explorer_Build_Convergence_Handoff.md` | `docs\reports\RHACO-CCX-20260905-001_Corpus_Explorer_Build_Convergence_Handoff.md` | 20507 | `ebcdc8bd9f383bfef74837e2e46381581269e3a9753fe08f1acabab79596a921` | `0af30ac8d7a0` | yes |
| `RHACO-CCX-20260905-002_Corpus_Explorer_M3_Harness_Evaluation_Handoff.md` | `docs\reports\RHACO-CCX-20260905-002_Corpus_Explorer_M3_Harness_Evaluation_Handoff.md` | 18984 | `9f777b57dbd26d9b59b1bd862af2a7a88d65917677c5b52670c7a5d27c702910` | `04c757392ee3` | yes |
| `RHACO-CCX-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep_Analysis_Handoff.md` | `docs\reports\RHACO-CCX-20260920-001_Corpus_Explorer_Public_Release_Readiness_Sweep_Analysis_Handoff.md` | 17846 | `51df211f2a40693c1cfb82a39aad7e70c6e7f4c7f04ee060e2b5b7ed43df24dd` | `827d6cefbf76` | yes |
| `RHACO-CHG-20260907-002_Build_Prompt_Template_v2_0_REF_Cut.md` | `docs\reports\RHACO-CHG-20260907-002_Build_Prompt_Template_v2_0_REF_Cut.md` | 55746 | `8fca64ae2c36e4110a66a1f76988ad4db5bba187bd70c2e2ae58f60a1bcb5956` | `c572eec9595d` | yes |
| `RHACO-CHG-20260907-004_Build_Prompt_Template_v2_1_REF_Cut.md` | `docs\reports\RHACO-CHG-20260907-004_Build_Prompt_Template_v2_1_REF_Cut.md` | 28879 | `7f2efd051e155de297bb55ea0aabd128268bcf131598b1a5a1c2ea78f8f04c66` | `3ed876a476cb` | yes |
| `RHACO-CHG-20260920-001_Build_Prompt_Template_v2_2_REF_Cut_Provenance_Correction.md` | `docs\reports\RHACO-CHG-20260920-001_Build_Prompt_Template_v2_2_REF_Cut_Provenance_Correction.md` | 16130 | `34fe674732c087f78ecdad55e4387c7348893a0945faf6aa5b2acd06320333d9` | `0c6deb7dd27a` | yes |
| `RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md` | `docs\reports\RHACO-CMP-20260903-001_Corpus_Explorer_Autonomous_Build_Harness.md` | 23880 | `2ab4c20b30b370c9b16637d5bb8709e8fa1ad79de58cfaec99d41f26b4dc93cb` | `55e3c0b875e6` | yes |
| `RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.md` | `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch.md` | 23306 | `ed01fa5412238767a55f30108844295a10bedc0ab6d1f7e5aca4c373c206ff6f` | `4c0efa9c6c41` | yes |
| `RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A1_Cap_Rehome_And_Session_2_Findings.md` | `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A1_Cap_Rehome_And_Session_2_Findings.md` | 9698 | `167771c75575ceef2d07e21a9fbfb6f00a24776ca619514cc9b9a216414be99a` | `c0c5f1cb4e4d` | yes |
| `RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A2_Convergence_Rulings_Ledger_And_Identity_Pin.md` | `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A2_Convergence_Rulings_Ledger_And_Identity_Pin.md` | 13899 | `34ee0c2dca4749f02082286bb1e20032c8ced34d9d12c17af66af6a6afd8fc15` | `98dd99b82d83` | yes |
| `RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A3_Criterion_6_Reconciliation_Mechanism_Correction.md` | `docs\handoffs\RHACO-HND-20260903-001_Corpus_Explorer_Autonomous_Build_Dispatch_Amendment_A3_Criterion_6_Reconciliation_Mechanism_Correction.md` | 3962 | `775d7b56b8b07373557931d9e4710bc28d34b590123007efcef8167811e13113` | `050b56970076` | yes |
| `RHACO_Build_Prompt_Template_Guide_v2_0.md` | `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_0.md` | 16639 | `c5146bf7676205dc9debec421ea1eecdd21468cb22f34b944d503e97eca3bc05` | `32f089c84274` | yes |
| `RHACO_Build_Prompt_Template_Guide_v2_1.md` | `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_1.md` | 18614 | `50c397f3bdf8418274d1a0a90e02961030367661270b1cdb3019a2c2e410c3c4` | `4045c8f92be1` | yes |
| `RHACO_Build_Prompt_Template_Guide_v2_2.md` | `docs\reference\RHACO_Build_Prompt_Template_Guide_v2_2.md` | 18839 | `000e2aa4a969385624d69bf6c010b441233c13feda8ec073b6d047fa0c8553fc` | `90b21b4c0193` | yes |
| `RHACO_Build_Prompt_Template_v2_0.md` | `docs\reference\RHACO_Build_Prompt_Template_v2_0.md` | 19562 | `3e248533091b21d955450cd836fe513e65d8523f1eb30f610770edb06125ec72` | `e348d05a7cb4` | yes |
| `RHACO_Build_Prompt_Template_v2_1.md` | `docs\reference\RHACO_Build_Prompt_Template_v2_1.md` | 22742 | `6ee71cf7a16a4b63927fb11f30bb8ab07f2ef7ea30c664711dc4f6fa131b5b2d` | `5896b2ed83cc` | yes |
| `RHACO_Build_Prompt_Template_v2_2.md` | `docs\reference\RHACO_Build_Prompt_Template_v2_2.md` | 24073 | `5ff7554cce30d41868e0c0da45ef1991ec637a1a812a29522e90164eed2001e8` | `afdbbdcb3bdb` | yes |
| `unfiled/PROMPT_TEMPLATE.md` | `working\PROMPT_TEMPLATE.md` | 7908 | `d1f2dee6dbdbc0a3ef13b3afceb468ef326347baeef98a2c8844763e23e7a36d` | `c9fd29c22281` | untracked at snapshot time |
| `unfiled/PROMPT_TEMPLATE_CHARTER.md` | `working\PROMPT_TEMPLATE_CHARTER.md` | 10153 | `7d6b39e138bcadd9a569890bb00751eb429b6987bfa5211f1dd68529654268fa` | `96410abb5181` | untracked at snapshot time |

## Upstream

`upstream/` holds the prompt this campaign's own build prompt was derived
from, and its licence, as they stand at the single commit
`aea8b1035030952555395de0c1de14ba693a1427` of the public repository
`rawprogress/fable-cities`.
