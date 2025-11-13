# Third-Party Notices (THIRD_PARTY_NOTICES.md)

This file centralizes third-party code notices, attributions and license metadata for components, snippets and other third-party content used in this repository.

IMPORTANT: I cannot verify remote repositories from this environment. The entries below include the original source URL and *action items* where a human maintainer must confirm the license (SPDX identifier), the exact commit SHA used, and any attribution obligations. Replace the "ACTION_REQUIRED" markers with the verified license and permalink before release.

---

## Template (for each entry)

- Component: Short name of the component or file used
- Used in: Repository path(s) where the code is used
- Source: URL to the original source
- Commit / Permalink: full commit SHA or permalink to the exact file/line used
- License: SPDX identifier and link to license text (or `ACTION_REQUIRED` if unknown)
- Modifications: Brief description of changes made relative to the original
- Notes: Additional obligations (attribution text, NOTICE file requirement, etc.)

---

## Entry: MDX syntax-highlighting example (msaoct/Mdxcontent-Portfolio)

- Component: MDX syntax-highlighting example / markdown-to-html helper
- Used in: frontend/ (examples/documentation)
- Source: https://github.com/msaoct/Mdxcontent-Portfolio/tree/5dece515245407549212a27d4817827e449700a7/codes-and-notes/convert-markdown-to-html-syntax-highlighting-nextjs-highlight-js-typescript.mdx
- Commit / Permalink: ACTION_REQUIRED — please provide the commit SHA or permalink used
- License: ACTION_REQUIRED — verify the upstream repository license and replace this with the SPDX identifier and a link to the license text
- Modifications: None recorded here — if code was copied, list exact files/lines and edits made
- Notes: If the upstream project is under a permissive license (MIT/Apache-2.0) include required attribution. If no license is present, do not ship copied code; either obtain permission or replace with original code under a known license.

---

## Entry: Next.js / Solana swap example (memochou1993/blog)

- Component: Next.js Solana swap example (blog post code snippet)
- Used in: frontend/ (documentation/citations)
- Source: https://github.com/memochou1993/blog/tree/38ea0079b09d7cb1a5d3bd76ae0816604b8991a6/source/_posts/2022/04/2022-04-22-%E5%9C%A8-Next-12-0-%E5%AF%A6%E4%BD%9C-Solana-%E5%8D%80%E5%A1%8A%E9%8F%88%E7%9A%84-Swap-%E4%BB%8B%E9%9D%A2.md
- Commit / Permalink: ACTION_REQUIRED — please provide the commit SHA or permalink used
- License: ACTION_REQUIRED — verify the upstream repository license and replace this with the SPDX identifier and a link to the license text
- Modifications: None recorded here — if code was copied, list exact files/lines and edits made
- Notes: If the upstream content is under a license requiring attribution or a NOTICE file (e.g., Apache-2.0), ensure the required notices are included in this repository.

---

## Verification actions required (maintainer)

1. For each `Source` above, visit the URL and confirm the repository license. Add the exact SPDX identifier and a link to the license file (for example, `MIT — https://github.com/owner/repo/blob/<sha>/LICENSE`).
2. For each used snippet or copied code, record the exact commit SHA or permalink to the file/lines used and add it to the "Commit / Permalink" field.
3. If any source has no license or an incompatible license, remove or replace the code before distribution and document the replacement here.
4. If the upstream license requires attribution or inclusion of license text (e.g., MIT), add the required attribution to this file or the repository `LICENSE`/NOTICE as appropriate.

If you want, I can attempt to fetch license files automatically (requires internet access from this environment). Otherwise, please perform the checks above and update this document.
