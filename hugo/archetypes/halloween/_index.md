---
title: '{{ replace .File.ContentBaseName `_` ` ` | title }}'
subtitle: Species common name
lastmod: {{ time.Format "31/01/2014" .Date }}

resources:
  - title: '{{ replace .File.ContentBaseName `_` ` ` | title }}'
    name: cover_image
    # Use relative path for a local image
    src: "https://placehold.co/600x400"
    params:
      attribution: CC-BY-SA
      link: "https://placehold.co/600x400"

layout: "species_intro"
weight: 1

params:
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
