{{ $scientificName := replace .File.ContentBaseName `_` ` ` | strings.FirstUpper }}
---
date: {{ .Date }}
title: {{ $scientificName }}
subtitle:
lastmod: {{ .Date }}

resources:
  - title: '{{ $scientificName }}'
    name: cover_image
    src: "placeholder.png"
    params:
      attribution: CC-BY-SA
      link: "https://placehold.co/600x400/png"

layout: "species_intro"
weight: 1

{{ $taxId := partial "halloween/FetchTaxId" $scientificName }}
params:
  lineage: {{ partial "halloween/LineageConfig" $taxId }}
  banner_title: "Species overview"
  goat_webpage: "https://goat.genomehubs.org"

  # Map
  gbif_taxon_id: 2874508
  latitude: 60
  longitude: -40
  initialZoom: 1.5

  # Optional
  iucn_category:
  iucn_link:
  swe_red_list:
  swe_red_list_link:
---

### Description

Write some content here in markdown for the introduction tab of the species page.

#### Genome reference

#### References

#### Changelog

- 31/10/2024 - Species first published on the Portal
