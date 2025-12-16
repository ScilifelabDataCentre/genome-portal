SHELL=/bin/bash
# Disable builtin implicit rules
MAKEFLAGS += -r

# SWG_* variables can be set in the process environment
SWG_CONFIG_DIR ?= config
SWG_DATA_DIR ?= data
SWG_INSTALL_DIR ?= hugo/static/data

CONFIG_DIR := $(SWG_CONFIG_DIR)
DATA_DIR := $(SWG_DATA_DIR)
INSTALL_DIR := $(SWG_INSTALL_DIR)

# To restrict operations to a subset of species, assign them as a
# comma-separated list to the SPECIES variable, either in the
# environment or as command-line option. Equivalent examples:
#
#     make SPECIES=linum_tenue,clupea_harengus build
#
#     export SPECIES=linum_tenue,clupea_harengue
#     make build
ifneq ($(strip $(SPECIES)),)
comma = ,
SPECIES_DIRS := $(addprefix $(CONFIG_DIR)/, $(sort $(subst $(comma), ,$(SPECIES))))
else
SPECIES_DIRS := $(CONFIG_DIR)
endif
# Determine TRIX data directories
ifeq ($(SPECIES_DIRS),$(CONFIG_DIR))
TRIX_DATA_DIRS := $(wildcard $(DATA_DIR)/*)
else
TRIX_DATA_DIRS := $(patsubst $(CONFIG_DIR)/%, $(DATA_DIR)/%, $(SPECIES_DIRS))
endif

CONFIGS := $(shell find $(SPECIES_DIRS) -type f -name 'config.yml')
JBROWSE_CONFIGS := $(patsubst $(CONFIG_DIR)/%,$(DATA_DIR)/%,$(CONFIGS:.yml=.json))

# Files to download for further processing (typically compressing and
# indexing).
#
# Each download target ends with a compression format
# extension, for example .zip, .gz or even .nozip when the file is not
# compressed.
export := SWG_DATA_DIR=$(SWG_DATA_DIR) SWG_CONFIG_DIR=$(SWG_CONFIG_DIR)
DOWNLOAD_TARGETS := $(shell $(export) ./scripts/make_download_targets $(CONFIGS) 2>/dev/null)
unzipped := $(basename $(DOWNLOAD_TARGETS))

# Fasta files and indices
FASTA := $(addsuffix .bgz, $(filter %.fna,$(unzipped)))
FASTA_INDICES := $(addsuffix .fai,$(FASTA))
FASTA_GZINDICES := $(FASTA_INDICES:.fai=.gzi)

# Fasta aliases
# One aliases.txt file per directory where we have an assembly
ALIASES := $(addsuffix aliases.txt,$(sort $(dir $(FASTA))))

# GFF files and indices
GFF := $(addsuffix .bgz, $(filter %.gff,$(unzipped)))
GFF_INDICES := $(addsuffix .csi,$(GFF))

# GTF files
GTF := $(filter %.gtf,$(unzipped))

# BED files
BED := $(addsuffix .bgz,$(filter %.bed,$(unzipped)))
BED_INDICES := $(addsuffix .csi,$(BED))

# trix files and subdirectories. Since trix indexing creates multiple files based on the assembly name, use wildcard to capture them.
TRIX_FILES := $(foreach dir,$(TRIX_DATA_DIRS),$(wildcard $(dir)/trix/*.ix*) $(wildcard $(dir)/trix/*_meta.json))

# Check if trix files match assembly names in config.json. Handles the case of updates to the assembly name
TRIX_OUTDATED := $(foreach dir,$(TRIX_DATA_DIRS),$(shell \
	if [ -f "$(dir)/config.json" ] && [ -d "$(dir)/trix" ]; then \
	    assemblies=$$(jq -r '.assemblies[].name' "$(dir)/config.json" 2>/dev/null | sort); \
	    trix_bases=$$(find "$(dir)/trix" -name '*.ix' 2>/dev/null | xargs -r -n1 basename | sed 's/\.ix$$//' | sort); \
	    if [ "$$assemblies" != "$$trix_bases" ]; then \
	        echo "$(dir)"; \
	    fi; \
	elif [ -d "$(dir)/trix" ] && [ ! -f "$(dir)/config.json" ]; then \
	    echo "$(dir)"; \
	fi \
))


TRIX_NEEDS_INDEXING := $(sort \
	$(foreach dir,$(TRIX_DATA_DIRS), \
	    $(if $(wildcard $(dir)/trix/*.ix),,$(dir)) \
	) \
	$(TRIX_OUTDATED))

LOCAL_FILES := $(GFF) $(GFF_INDICES) \
	$(FASTA) $(FASTA_INDICES) $(FASTA_GZINDICES) \
	$(GTF) \
	$(BED) $(BED_INDICES) \
	$(ALIASES) \
	$(TRIX_FILES)

# Files to install
INSTALLED_FILES := $(patsubst $(DATA_DIR)/%,$(INSTALL_DIR)/%, $(LOCAL_FILES) $(JBROWSE_CONFIGS))

# Formatting
INFO := '\x1b[0;46m'
RESET := '\x1b[0m'

define greet
$(info $(shell printf '%*s\U1f43f%s\n' 30 '** ' '  **'))
endef

define log_info
	printf $(INFO)$(1)$(RESET)'\n'
endef

define log_list
	printf $(1)"\n"
	printf "  - %s\n" $(sort $(2))
endef
.PHONY: all
all: build install
	$(greet)

.PHONY: build
build: download recompress index aliases jbrowse-config ensure-trix-config text-index

.PHONY: debug
debug:
	$(call log_list, "Configuration directories: ", $(SPECIES_DIRS))
	$(call log_list, "Configuration files:", $(CONFIGS))
	$(call log_list, "JBrowse configuration files:", $(JBROWSE_CONFIGS))
	$(call log_list, "Files to download:", $(DOWNLOAD_TARGETS))
	$(call log_list, "Recompressed files:", $(FASTA) $(GFF) $(GTF) $(BED))
	$(call log_list, "FASTA indices:", $(FASTA_INDICES) $(FASTA_GZINDICES))
	$(call log_list, "GFF indices:", $(GFF_INDICES))
	$(call log_list, "BED indices:", $(BED_INDICES))
	$(call log_list, "Trix indices:", $(TRIX_FILES))
	$(call log_list, "Files to install:", $(INSTALLED_FILES))

.PHONY:
aliases: $(ALIASES)
	$(call log_info, "Generated aliases ", $(ALIASES))

.PHONY: clean-aliases
clean-aliases:
	@rm -f $(ALIASES)

# Trix writes to files in <SPECIES_NAME>/trix and to config.json. 
# Thus, all those files needs to be removed in the cleanup
.PHONY: clean-trix
clean-trix: clean-config
	@rm -f $(TRIX_FILES)

.PHONY: jbrowse-config
jbrowse-config: $(JBROWSE_CONFIGS)
	$(call log_info,'Generated JBrowse configuration in directories')
	@printf "  - %s\n" $(JBROWSE_CONFIGS:/config.json=)


.PHONY: download
download: $(DOWNLOAD_TARGETS)
	$(call log_info,'Downloaded data files')
	@printf "  - %s\n" $?


# Remove downloaded copies of remote files
.PHONY: clean-upstream
clean-upstream:
	rm -f $(DOWNLOAD_TARGETS)

# Remove JBrowse configuration files
.PHONY: clean-config
clean-config:
	rm -f $(JBROWSE_CONFIGS)

# Remove built data files
.PHONY: clean-local
clean-local:
	rm -f $(LOCAL_FILES)

# Remove all artifacts
.PHONY: clean
clean: clean-upstream clean-local clean-config clean-trix

.PHONY: recompress
recompress: $(GFF) $(FASTA) $(GTF) $(BED);

# Copy data and configuration to hugo static folder
.PHONY: install
install: $(INSTALLED_FILES) install-trix;

$(INSTALLED_FILES): $(INSTALL_DIR)/%: $(DATA_DIR)/%
	@echo "Installing $*"
	@mkdir -p $(@D)
	@cp $< $@

# Remove JBrowse data and configuration from hugo static folder
.PHONY: uninstall
uninstall:
	rm -f $(INSTALLED_FILES)

.PHONY: index
index: $(FASTA_INDICES) $(GFF_INDICES) $(BED_INDICES)
ifneq ($(FASTA_INDICES),)
	$(call log_info,'Indexed FASTA files')
	@printf '  - %s\n' $(FASTA_INDICES:.fai='.{fai,gzi}')
endif
ifneq ($(GFF_INDICES),)
	$(call log_info,'Indexed GFF files')
	@printf '  - %s\n' $(GFF_INDICES)
endif
ifneq ($(BED_INDICES),)
	$(call log_info,'Indexed BED files')
	@printf '  - %s\n' $(BED_INDICES)
endif

define make_index
	@$(SHELL) scripts/index $<
endef

$(GFF_INDICES) $(BED_INDICES): %.csi: %
	$(make_index)

$(FASTA_INDICES): %.fai: %
	$(make_index)

$(JBROWSE_CONFIGS): $(DATA_DIR)/%/config.json: $(CONFIG_DIR)/%/config.yml $(CONFIG_DIR)/%/config.json
	@echo "Generating JBrowse configuration for $*"; \
	cp $(lastword $^) $@ && \
	$(SHELL) scripts/generate_jbrowse_config $@ $<; \
	if [ -d "$(DATA_DIR)/$*/trix" ] && [ -n "$$(find $(DATA_DIR)/$*/trix -name '*.ix' 2>/dev/null)" ]; then \
		has_adapters=$$(jq -e '.aggregateTextSearchAdapters | length > 0' "$@" 2>/dev/null || echo "false"); \
		if [ "$$has_adapters" != "true" ]; then \
			echo "Reconstructing aggregateTextSearchAdapters from trix files for $*"; \
			$(SHELL) scripts/reconstruct_trix_config_if_trix_files_exist "$@" "$(DATA_DIR)/$*/trix"; \
		fi; \
	fi


$(CONFIG_DIR)/%/config.json:
	@echo '{}' > $@


# Order-only prerequisite to avoid re-downloading everything if data/.downloads
# directory gets accidentally deleted. Downside: if an upstream file changes,
# the local outdated copy must be deleted before running `make download`
$(DOWNLOAD_TARGETS): $(DATA_DIR)/%:| $(DATA_DIR)/.downloads/%
	@echo "Downloading $@ ..."; \
	mkdir -p --mode=0755 $(@D) && \
	url="$$(< $|)"; \
	case "$$url" in \
		https://figshare.scilifelab.se/*) \
			curl -# -f -L -A "Mozilla/5.0" --output $@ "$$url" ;; \
		*) \
			curl -# -f -L --output $@ "$$url" ;; \
	esac

# Recompress downloaded files using bgzip(1).
#
# File-type-specific transformations that need to occur before
# recompression may be implemented in scripts/filter
#
# Use a variable to properly escape
# pattern character. Using \% does not work well with secondary
# expansion
_pattern = %
.SECONDEXPANSION:
$(FASTA) $(GFF) $(BED): %.bgz: $$(filter $$*$$(_pattern),$$(DOWNLOAD_TARGETS))
	@$(SHELL) -o pipefail -c "zcat -f < $< | ./scripts/filter $(<F) | bgzip > $@"

$(GTF): $$(filter $$@$$(_pattern),$$(DOWNLOAD_TARGETS))
	@$(SHELL) -o pipefail -c "zcat -f < $< > $@"

# The prerequisites of an alias file are all the FASTA files
# downloaded in the same species directory.
$(ALIASES): %/aliases.txt: $$(filter $$*$$(_pattern),$$(FASTA))
	@echo "[aliases] Generating aliases from $^" >&2
	@$(SHELL) ./scripts/aliases $^ > $@

TRIX_INSTALLED := $(patsubst $(DATA_DIR)/%/trix/%, $(INSTALL_DIR)/%/trix/%, $(TRIX_FILES))

.PHONY: ensure-trix-config
ensure-trix-config: $(JBROWSE_CONFIGS)
	@for dir in $(TRIX_DATA_DIRS); do \
	    if [ -f "$$dir/config.json" ] && [ -d "$$dir/trix" ] && [ -n "$$(find $$dir/trix -name '*.ix' 2>/dev/null)" ]; then \
	        if ! jq -e '.aggregateTextSearchAdapters | length > 0' "$$dir/config.json" > /dev/null 2>&1; then \
	            echo "Reconstructing aggregateTextSearchAdapters for $$(basename $$dir)"; \
	            $(SHELL) scripts/reconstruct_trix_config_if_trix_files_exist "$$dir/config.json" "$$dir/trix"; \
	        fi; \
	    fi; \
	done

# Trix-indexing of the protein coding genes track to enable searching for gene names in JBrowse
# It needs to read the config.json file generated by the build recipe
.PHONY: text-index
text-index: $(JBROWSE_CONFIGS)
	@for dir in $(TRIX_NEEDS_INDEXING); do \
	    if [ -d "$$dir" ] && [ -f "$$dir/config.json" ]; then \
	        $(call log_info,'Checking for trix indexes '); \
	        if [ -d "$$dir/trix" ]; then \
	            rm -rf "$$dir/trix"; \
	        fi; \
	        jbrowse text-index --target "$$dir"; \
	    fi; \
	done
	@if [ -n "$(TRIX_NEEDS_INDEXING)" ]; then \
	    printf '\x1b[0;46mGenerated trix index files\x1b[0m\n'; \
	else \
	    printf '\x1b[0;46mAll trix index files up to date\x1b[0m\n'; \
	fi
	@for dir in $(TRIX_DATA_DIRS); do \
	    find "$$dir/trix" -type f -name '*.ix*' -or -name '*_meta.json' 2>/dev/null | sort; \
	done

# Install the trix files in the destination directory

$(INSTALL_DIR)/%/trix/%: $(DATA_DIR)/%/trix/%
	@mkdir -p $(@D)
	@cp $< $@

install-trix: $(TRIX_INSTALLED)
