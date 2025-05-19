---
# The params below were auto-generated, you should not need to edit them...
# unless you were warned by the add-new-species.py script.
title: "*${species_name}*"
subtitle: "${common_name}"
last_updated: "${todays_date}" # format DD/MM/YYYY

layout: "species_intro"
banner_title: "Species overview"
weight: 1

url: "${species_slug}"
science_name: "${species_name}"
lineage_data_path: "${species_slug}/taxonomy"

cover_image: "/img/species/${species_slug}.webp"
img_attrib_text: "${img_attrib_text}"
img_attrib_link: "${img_attrib_link}"

gbif_taxon_id: "${gbif_taxon_id}"
goat_webpage: "${goat_webpage}"

# These 3 params define the initial view for the map
# latitude and longitude are for the map center.
# If you don't want to include an observation map, remove these params
latitude: 0
longitude: 0
initialZoom: 1

# Optional params below,
# comment them in if you want to include them.
# iucn_category: "[EDIT]"
# iucn_link: "[EDIT]"

# swe_red_list: "[EDIT]"
# swe_red_list_link: "[EDIT]"
---

### Description

${description}


#### How to cite

If you use the data presented in the genome portal from this species in your research, please cite the original publication:

```{style=citation}
${publication}
```

If you have used the pages for this species in the Genome Portal, please refer to it in-text as: "The *${species_name}* entry in the Swedish Reference Genome Portal (Retrieved <span class="todays-date"></span>)." and use the following for the bibliography:

```{style=citation}
Swedish Reference Genome Portal (Retrieved DATE_ACCESSED), SciLifeLab Data Centre, version VERSION_NUMBER from <https://genomes.scilifelab.se>, [RRID:SCR_026008](https://rrid.site/data/record/nlx_144509-1/SCR_026008/resolver?q=rrid:scr_026008)
```

#### References

${references}


#### Changelog

- ${todays_date} - Species first published on the Portal