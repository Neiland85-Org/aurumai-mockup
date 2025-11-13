# Third-Party Notices (THIRD_PARTY_NOTICES)

This file centralizes third-party code notices, attributions and license metadata for components, snippets and other third-party content used in this repository.

Template header for each entry (fill for every component):

- Component: Short name of the component or file used
- Used in: Repository path(s) where the code is used
- Source: URL to the original source + permalink or commit SHA used
- License: Exact license name and link to license text (or "UNKNOWN - verify before release")
- Modifications: Brief description of changes made relative to the original
- Notes: Any additional compliance notes or obligations (e.g., attribution text required)

---

## Entry: convert-markdown-to-html syntax-highlighting example

- Component: Next.js MDX syntax-highlighting example (code snippet reference)
- Used in: frontend/ (pages, config & examples)
- Source: https://github.com/msaoct/Mdxcontent-Portfolio/tree/5dece515245407549212a27d4817827e449700a7/codes-and-notes/convert-markdown-to-html-syntax-highlighting-nextjs-highlight-js-typescript.mdx
- License: UNKNOWN — please verify upstream repository license and provide exact SPDX identifier and link. If no license is available, obtain permission or remove/replace the code with an alternative under a compatible license.
- Modifications: N/A — repository currently references snippets; any actual copied code should be listed here once identified.
- Notes: The original citation previously contained a partial package.json fragment; that fragment has been removed from this notice. See `frontend/package.json` for actual project configuration.

---

## Entry: Next.js / Solana swap example

- Component: Next.js Solana swap example (reference)
- Used in: frontend/ (documentation/citations)
- Source: https://github.com/memochou1993/blog/tree/38ea0079b09d7cb1a5d3bd76ae0816604b8991a6/source/_posts/2022/04/2022-04-22-%E5%9C%A8-Next-12-0-%E5%AF%A6%E4%BD%9C-Solana-%E5%8D%80%E5%A1%8A%E9%8F%88%E7%9A%84-Swap-%E4%BB%8B%E9%9D%A2.md
- License: UNKNOWN — please verify upstream repository license and provide exact SPDX identifier and link. If no license is available, obtain permission or remove/replace the code with an alternative under a compatible license.
- Modifications: N/A — remove partial package.json fragments from citations; see `frontend/package.json` for configuration instead.
- Notes: The previous citations included partial JSON snippets; these were removed to avoid duplication and to keep license/attribution metadata in a single place.

---

Notes about verification:

- I (the automated maintainer) cannot fetch remote license files from the internet in this environment. You should verify each `Source` URL above and add the exact license (e.g., MIT, Apache-2.0) and the commit SHA used.
- If any source has no license, you must either remove the borrowed code or replace it with a compatible replacement, or obtain a license/permission from the author.

If you want, I can:

- Attempt to fetch and add license info automatically if you allow internet access, or
- Provide suggested replacements (small code snippets under compatible open source licenses) for any unlicensed code.
