# University LaTeX Template Analysis

Template inspected: `Latex-Luigi vanvitelli/` (renamed after migration to `Latex-Luigi-Vanvitelli/` to match the prompt and README)

Note: at the start of inspection the prompt referred to `Latex-Luigi-Vanvitelli/`, while the project contained the template under `Latex-Luigi vanvitelli/`.

## 1. Document Class

The template main file, `thesis_main.tex`, uses:

```latex
\documentclass[12pt, twoside]{report}
```

The template also bundles the `extsizes` package/classes (`extarticle`, `extreport`, `extbook`, etc.) for non-standard font sizes, but the provided thesis template does not use them. The active class is the standard `report` class with `12pt` and `twoside`.

Required or template-included packages:

- `geometry` with `a4paper, margin=3.3cm`
- `babel` with `english`
- `lipsum` for sample filler text
- `fancyhdr` for headers
- `biblatex` with `style=alphabetic`
- `csquotes`
- `graphicx`
- `listings`
- `xcolor`
- `vanvfrontespizio` for the university title page/frontespizio

The custom `vanvfrontespizio.sty` itself requires:

- `setspace`
- `etoolbox`
- `tikz`
- TikZ library `backgrounds`

## 2. Structure Requirements

The template uses the `report` hierarchy:

- `\chapter`
- `\section`
- `\subsection`
- lower levels inherited from `report`

In the sample template, chapter headings are created in the main file and the chapter body is inserted afterward:

```latex
\chapter{Introduction}
\input{Chapters/introduction}
```

The sample chapter files are mostly empty/body-only, except for frontmatter-style files such as `summary.tex` and `acknowledgments.tex`, which use unnumbered chapter headings.

Template frontmatter/order:

1. `\input{titlepage}` containing `\makefrontpage`
2. `\nocite{*}` in the sample file
3. `\input{Chapters/dedication}`
4. `\input{Chapters/acknowledgments}`
5. `\input{Chapters/summary}`
6. `\pagestyle{empty}`
7. `\tableofcontents`
8. `\pagestyle{fancy}`

The template does not explicitly include a declaration page, list of figures, or list of tables. It does include a dedication placeholder, acknowledgements, and summary. For this project, the closest mapping is:

- title page -> `frontmatter/titlepage.tex`
- declaration -> retained as an added project requirement, although not present in the template
- acknowledgements -> `frontmatter/acknowledgements.tex`
- summary/abstract -> `abstract.tex`
- table of contents
- optional list of figures/tables from the current project

Template backmatter:

- A manually created unnumbered appendix heading in the sample:

```latex
\chapter*{Appendx}
\input{Chapters/appendix}
```

- Bibliography printed with:

```latex
\printbibliography
```

The sample has a typo, `Appendx`, and does not use `\appendix`. The current project already has a proper appendix chapter file, so migration should avoid duplicating or misspelling the appendix heading.

## 3. Citation and Bibliography Style

The template uses `biblatex`, not `natbib` or classic BibTeX:

```latex
\usepackage[style=alphabetic]{biblatex}
\usepackage{csquotes}
\addbibresource{references.bib}
...
\printbibliography
```

Citation style:

- Alphabetic bibliography labels through `style=alphabetic`.
- The template sample does not demonstrate in-text citation commands.
- Native `biblatex` commands include `\cite`, `\parencite`, and `\textcite`.

Current project citation commands:

- Current `main.tex` uses `natbib`:

```latex
\usepackage[numbers,sort&compress]{natbib}
\bibliographystyle{plainnat}
\bibliography{writing/references}
```

- Current chapters use `\citet` and `\citep` extensively.

Migration implication:

- Switching to template-native `biblatex` without compatibility would break existing chapter citations.
- To preserve chapter files exactly and still use the template bibliography system, `biblatex` should be loaded with `natbib=true`:

```latex
\usepackage[style=alphabetic,natbib=true]{biblatex}
```

- Citation migration should still be flagged because the project uses natbib-style `\citet`/`\citep`, while the template is biblatex-based.

## 4. Fonts and Typography

Template typography:

- Standard Computer Modern/LaTeX default fonts; no explicit font family package is used.
- Document class is `12pt`.
- Page size/margins:

```latex
\usepackage[a4paper, margin=3.3cm]{geometry}
```

- The front page uses `setspace` internally, with title-page blocks at `1.2`, `2`, and `1` line spacing.
- The template does not set global `\onehalfspacing`; the current project does.

Current project typography differences:

- Current `main.tex` uses `\usepackage[margin=1in]{geometry}`.
- Current `main.tex` uses `\onehalfspacing`.
- Current `main.tex` loads `inputenc` and `fontenc`; the template does not. These are usually harmless under pdfLaTeX and useful for accented text.

## 5. Figures and Tables

Template figure/table setup:

- Loads `graphicx`.
- Sets:

```latex
\graphicspath{ {./images/} }
```

- No custom caption package or caption style is defined.
- No explicit figure/table placement rules beyond LaTeX defaults.
- No `booktabs`, `array`, `longtable`, or table-specific packages are included by the template.

Current project needs:

- `\graphicspath{{figures/}}`
- `array` because generated tables use `>{\raggedright\arraybackslash}p{...}`
- `booktabs` because several generated tables use `\toprule`, `\midrule`, and `\bottomrule`
- `amsmath` for mathematical notation
- `hyperref` for links and references

Migration implication:

- Keep template packages and add current project packages needed by existing chapter/table content.

## 6. Title Page

The title page is produced by `vanvfrontespizio` using field-setting commands in the preamble, then `\makefrontpage`.

Template title-page fields/commands:

- `\Universita{...}`
- `\Facolta{...}` optional; sample is commented out
- `\Dipartimento{...}`
- `\CorsoDiLaurea{...}`
- `\Materia{...}` optional
- `\AnnoAccademico{...}`
- `\Titolo{...}`
- `\Relatore{...}`
- `\RelatoreLabel{...}` optional
- `\Correlatore{...}` optional, repeatable
- `\CorrelatoreLabel{...}` optional
- `\Candidato{...}`
- `\CandidatoLabel{...}` optional
- `\Matricola{...}`
- `\Logo{...}`
- `\LogoWidth{...}` optional
- `\LogoPosition{...}` optional: `top`, `below-uni`, `above-title`, `below-title`, or `no-logo`

Sample field labels:

- University: `Università degli Studi della Campania ``Luigi Vanvitelli''`
- Department: `Dipartimento di Matematica e Fisica`
- Degree course: `Bachelor's degree in Data Analytics`
- Academic year: `AY 20XX--20XX`
- Supervisor label: `Supervisor`
- Co-supervisor label: `Co-supervisor`
- Candidate label default: `Candidate`

Project-specific required values from the prompt:

- University: `Università degli Studi della Campania Luigi Vanvitelli`
- Degree: `MSc in Data Science`
- Academic year: `2025--2026`
- Candidate: `Mahdi Mohammadzadeh`
- Supervisor: `% TODO: Mahdi must fill this in manually`
- Department/Faculty: `% TODO: Mahdi must confirm official name`

## 7. Differences from Current `main.tex`

Structural differences:

- Template uses `\documentclass[12pt, twoside]{report}`; current uses `\documentclass[12pt,a4paper]{report}`.
- Template sets A4 paper through `geometry`; current sets A4 paper as a class option.
- Template margin is `3.3cm`; current margin is `1in`.
- Template uses `biblatex` and `\printbibliography`; current uses `natbib`, `plainnat`, and `\bibliography`.
- Template configures title-page metadata in the preamble with `vanvfrontespizio`; current uses custom `\thesistitle`, `\thesisauthor`, etc.
- Template title page uses `\makefrontpage`; current title page manually typesets fields.
- Template sample has dedication, acknowledgements, summary, TOC; current has title page, declaration, acknowledgements, abstract, TOC, list of figures, list of tables.
- Template creates chapter headings in `thesis_main.tex`; current chapter files already include `\chapter{...}`.
- Template sample uses `\chapter*{Appendx}` and `\input{Chapters/appendix}`; current uses `\appendix` and inputs a chapter file that already contains `\chapter{Appendix}`.
- Template sets `\pagestyle{fancy}` with page/mark headers; current does not use `fancyhdr`.
- Template has code-listing setup with `listings` and `xcolor`; current does not.

Packages in the template not currently in `main.tex`:

- `babel`
- `lipsum`
- `fancyhdr`
- `biblatex`
- `csquotes`
- `listings`
- `xcolor`
- `vanvfrontespizio`
- `tikz` indirectly via `vanvfrontespizio`
- `etoolbox` indirectly via `vanvfrontespizio`

Packages in current `main.tex` not in the template:

- `inputenc`
- `fontenc`
- `array`
- `booktabs`
- `amsmath`
- `setspace` directly, although indirectly required by `vanvfrontespizio`
- `natbib`
- `hyperref`

Potential conflicts:

- `natbib` conflicts conceptually and often technically with `biblatex`. It should be removed and replaced with `biblatex` using `natbib=true` if `\citep` and `\citet` must remain unchanged.
- `plainnat`/`\bibliography` should not be used with `biblatex`; use `\addbibresource{writing/references.bib}` and `\printbibliography`.
- The template's `\graphicspath{ {./images/} }` would not find current figures; use `\graphicspath{{figures/}}`.
- Adding `\chapter{...}` wrappers in `main.tex` would duplicate current chapter headings.

## 8. Migration Plan

Exact migration steps:

1. Copy required template assets to the project root:
   - `vanvfrontespizio.sty`
   - `Vanv-logo.png`
2. Rewrite `main.tex` to:
   - use `\documentclass[12pt, twoside]{report}`
   - use template geometry: `a4paper, margin=3.3cm`
   - load template packages
   - keep project-required packages for existing content: `inputenc`, `fontenc`, `array`, `booktabs`, `amsmath`, `hyperref`
   - replace `natbib` with `biblatex` using `style=alphabetic,natbib=true`
   - use `\addbibresource{writing/references.bib}`
   - configure `vanvfrontespizio` fields in the preamble
   - input frontmatter in the selected order: title page, declarations, acknowledgements, abstract, TOC, LOF, LOT
   - input chapter files directly, without adding chapter wrappers
   - use `\appendix` before `chapters/appendix`
   - end with `\printbibliography`
3. Rewrite `frontmatter/titlepage.tex` to call `\makefrontpage` using the template front-page package.
4. Update `frontmatter/declarations.tex`, `frontmatter/acknowledgements.tex`, and `abstract.tex` to use unnumbered chapter-style frontmatter formatting compatible with the template.
5. Do not edit `chapters/*.tex` in this migration, because the prompt requires preserving chapter content exactly.
6. Create `outputs/citation_migration_needed.txt` noting that current chapter citations are natbib-style while the template is biblatex-based.
7. Compile with `latexmk -pdf main.tex`; if unavailable, use the LaTeX compile fallback. Attempt up to three fixes for common missing-package/path/undefined-command issues.
8. Update repository packaging files:
   - `.gitignore`
   - `README.md`
   - `thesis_overleaf_upload.zip`

Files to replace or modify:

- `main.tex`
- `frontmatter/titlepage.tex`
- `frontmatter/declarations.tex`
- `frontmatter/acknowledgements.tex`
- `abstract.tex`
- `.gitignore`
- `README.md`
- root-level copied template files: `vanvfrontespizio.sty`, `Vanv-logo.png`

Chapter structural changes:

- No chapter files should be changed now.
- No structural change is required inside chapter files for this migration because they already contain `\chapter` headings.
- A future cleanup could move `\chapter` commands from chapter files into `main.tex` to match the template sample more literally, but that would violate the current instruction to preserve chapter content exactly.
