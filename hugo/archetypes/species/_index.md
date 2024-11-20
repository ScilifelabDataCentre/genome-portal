{{- $scientificName := replace .File.ContentBaseName `_` ` ` | strings.FirstUpper -}}
---
date: {{ .Date }}
title: {{ $scientificName }}
subtitle:
lastmod: {{ .Date }}

type: species_bundle
layout: "species_intro"
weight: 1

resources:
  - title: '{{ $scientificName }}'
    name: cover_image
    src: "placeholder.png"
    params:
      attribution: CC-BY-SA
      link: "https://placehold.co/600x400/png"

{{ $taxId := partial "species_bundle/GetTaxId" $scientificName }}
lineage: {{ partial "species_bundle/LineageConfig" $taxId }}
# Use this setting to override the default taxonomy ranks to display.
# See config/_default/params.yaml for the syntax to use.
taxonomy_ranks:
params:
  banner_title: "Species overview"
  goat_webpage: '{{ printf
  "https://goat.genomehubs.org/record?recordId=%s&result=taxon&taxonomy=ncbi"
  $taxId
  }}'

  # Map
  gbif_taxon_id: {{ partial "species_bundle/GetGbifKey.html" $scientificName }}
  latitude: 0
  longitude: 0
  initialZoom: 1

  # Optional
  iucn_category:
  iucn_link:
  swe_red_list:
  swe_red_list_link:
---

### Description

#### Genome reference

#### References

#### Changelog

- {{ .Date | time.Format ":date_medium" }} - Species first published on the Portal
