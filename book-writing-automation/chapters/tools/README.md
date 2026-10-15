# Markdown → .docx for the manuscript

Converts a chapter's markdown into a Word file with real Heading 1/2/3 styles,
US Letter pages, 1-inch margins and footer page numbers.

    npm install docx            # once, anywhere; the script needs `docx` resolvable
    node tools/md2docx.js chapter-13-trust-at-scale.md ./docx
    python3 tools/repack.py "docx/*.docx"

`repack.py` is required. The `docx` npm package writes `[Content_Types].xml` as the
LAST zip entry; Word tolerates that, but strict OPC readers (LibreOffice, some
converters) refuse to open the file. `repack.py` rewrites the archive with
`[Content_Types].xml` first and drops the bare directory entries.
