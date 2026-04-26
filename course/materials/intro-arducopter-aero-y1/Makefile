# Makefile — material-builder artifacts for course intro-arducopter-aero-y1
#
# Builds student + instructor versions of every artifact into build/.
# Single .tex source per artifact, gated via shared/version-flags.tex.
# Toolchain: pdflatex (locked).

PDFLATEX        := pdflatex
PDFLATEX_FLAGS  := -interaction=nonstopmode -halt-on-error -file-line-error
INSTRUCTOR_DEF  := \def\instructorversion{}

BUILDDIR        := build

SLIDES_SRC      := slides/day1.tex slides/day2.tex
SLIDE_BASES     := day1 day2

HANDOUT_BASES   := student instructor
CHEATSHEET_BASE := cheatsheet

LAB_BASES       := l1-first-sitl-launch l2-first-flight l3-closing-lab

.PHONY: all slides handouts cheatsheet lab-guides clean distclean

all: slides handouts cheatsheet lab-guides

# -----------------------------------------------------------------------------
# Slides — one source per day (day1.tex, day2.tex). Each compiled twice per
# version: student build is the bare-input form; instructor build prepends
# \def\instructorversion{}. Two passes to settle TOC / overlay refs.
# -----------------------------------------------------------------------------
slides: $(addprefix $(BUILDDIR)/slides/,$(addsuffix -student.pdf,$(SLIDE_BASES))) \
        $(addprefix $(BUILDDIR)/slides/,$(addsuffix -instructor.pdf,$(SLIDE_BASES)))

$(BUILDDIR)/slides/%-student.pdf: slides/%.tex shared/preamble.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/slides
	@echo "[slides:student] $*"
	@cd slides && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/slides -jobname=$*-student $*.tex >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/slides -jobname=$*-student $*.tex >/dev/null

$(BUILDDIR)/slides/%-instructor.pdf: slides/%.tex shared/preamble.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/slides
	@echo "[slides:instructor] $*"
	@cd slides && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/slides -jobname=$*-instructor "$(INSTRUCTOR_DEF)\input{$*.tex}" >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/slides -jobname=$*-instructor "$(INSTRUCTOR_DEF)\input{$*.tex}" >/dev/null

# -----------------------------------------------------------------------------
# Handouts — one body (handout-body.tex), two thin launchers (student.tex,
# instructor.tex). Compiled directly from handouts/.
# -----------------------------------------------------------------------------
handouts: $(BUILDDIR)/handouts/student.pdf $(BUILDDIR)/handouts/instructor.pdf

$(BUILDDIR)/handouts/student.pdf: handouts/student.tex handouts/handout-body.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/handouts
	@echo "[handout:student]"
	@cd handouts && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/handouts -jobname=student student.tex >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/handouts -jobname=student student.tex >/dev/null

$(BUILDDIR)/handouts/instructor.pdf: handouts/instructor.tex handouts/handout-body.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/handouts
	@echo "[handout:instructor]"
	@cd handouts && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/handouts -jobname=instructor instructor.tex >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/handouts -jobname=instructor instructor.tex >/dev/null

# -----------------------------------------------------------------------------
# Cheatsheet — single body (cheatsheet-body.tex), student build = direct,
# instructor build = inline \def.
# -----------------------------------------------------------------------------
cheatsheet: $(BUILDDIR)/cheatsheet/cheatsheet-student.pdf $(BUILDDIR)/cheatsheet/cheatsheet-instructor.pdf

$(BUILDDIR)/cheatsheet/cheatsheet-student.pdf: cheatsheet/cheatsheet.tex cheatsheet/cheatsheet-body.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/cheatsheet
	@echo "[cheatsheet:student]"
	@cd cheatsheet && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/cheatsheet -jobname=cheatsheet-student cheatsheet.tex >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/cheatsheet -jobname=cheatsheet-student cheatsheet.tex >/dev/null

$(BUILDDIR)/cheatsheet/cheatsheet-instructor.pdf: cheatsheet/cheatsheet.tex cheatsheet/cheatsheet-body.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/cheatsheet
	@echo "[cheatsheet:instructor]"
	@cd cheatsheet && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/cheatsheet -jobname=cheatsheet-instructor "$(INSTRUCTOR_DEF)\input{cheatsheet.tex}" >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/cheatsheet -jobname=cheatsheet-instructor "$(INSTRUCTOR_DEF)\input{cheatsheet.tex}" >/dev/null

# -----------------------------------------------------------------------------
# Lab guides — one source per lab (lab-guides/<slug>.tex), gated student vs
# instructor by the same \def\instructorversion{} pattern as slides + cheatsheet.
# -----------------------------------------------------------------------------
lab-guides: $(addprefix $(BUILDDIR)/lab-guides/,$(addsuffix -student.pdf,$(LAB_BASES))) \
            $(addprefix $(BUILDDIR)/lab-guides/,$(addsuffix -instructor.pdf,$(LAB_BASES)))

$(BUILDDIR)/lab-guides/%-student.pdf: lab-guides/%.tex shared/preamble.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/lab-guides
	@echo "[lab-guide:student] $*"
	@cd lab-guides && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/lab-guides -jobname=$*-student $*.tex >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/lab-guides -jobname=$*-student $*.tex >/dev/null

$(BUILDDIR)/lab-guides/%-instructor.pdf: lab-guides/%.tex shared/preamble.tex shared/macros.tex shared/version-flags.tex | $(BUILDDIR)/lab-guides
	@echo "[lab-guide:instructor] $*"
	@cd lab-guides && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/lab-guides -jobname=$*-instructor "$(INSTRUCTOR_DEF)\input{$*.tex}" >/dev/null && \
	  $(PDFLATEX) $(PDFLATEX_FLAGS) -output-directory=../$(BUILDDIR)/lab-guides -jobname=$*-instructor "$(INSTRUCTOR_DEF)\input{$*.tex}" >/dev/null

# -----------------------------------------------------------------------------
# Build dirs
# -----------------------------------------------------------------------------
$(BUILDDIR)/slides $(BUILDDIR)/handouts $(BUILDDIR)/cheatsheet $(BUILDDIR)/lab-guides:
	@mkdir -p $@

clean:
	rm -rf $(BUILDDIR)
	find . -name '*.aux' -o -name '*.log' -o -name '*.toc' -o -name '*.nav' -o -name '*.snm' -o -name '*.out' -o -name '*.synctex.gz' -o -name '*.vrb' | xargs -r rm -f

distclean: clean
