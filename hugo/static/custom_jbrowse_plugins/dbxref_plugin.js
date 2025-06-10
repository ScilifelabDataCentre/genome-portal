export default class DbxrefPlugin {
  name = 'SRGP-DbxrefPlugin'
  version = '1.0.0'

  install() {}

  configure(pluginManager) {
    /**
    * Generates clickable links in the feature detailspanel for a given FeatureTrack that is annotated with dbxref annotation.
    * Implementation is based on the example provided in the JBrowse 2 docs: 
    * https://jbrowse.org/jb2/docs/config_guides/customizing_feature_details/
    * 
    * It takes a feature object from a FeatureTrack as input 
    * and returns a string with HTML links for dbxrefs, ontology terms, and UniProt IDs.
    * This is rendered as a hyperlink in the feature details panel of the track.
    * 
    * To apply to a track, add the following to a track in a species config.json: 
    * {"tracks": [{ [...] "formatDetails": {"subfeatures": "jexl:{dbxref:dbxrefLinkout(feature), ontology_term:ontologyLinkout(feature), uniprot_id:uniprotLinkout(feature)}"}}]}
    * 
    * See also PR101 at https://github.com/ScilifelabDataCentre/genome-portal/pull/101 for a use-case example.
    */
    pluginManager.jexl.addFunction('dbxrefLinkout', feature => {
      if (!feature.dbxref) {
        return ''
      }

      const dbxrefs = Array.isArray(feature.dbxref)
        ? feature.dbxref
        : [feature.dbxref]

      return dbxrefs.map(dbxref => {
        if (dbxref.startsWith('InterPro:')) {
          const ref = dbxref.replace('InterPro:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('CDD:')) {
          const ref = dbxref.replace('CDD:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/cdd/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('FunFam:')) {
          // Example: FunFam:G3DSA:2.60.40.60:FF:000066
          const parts = dbxref.split(':')
          if (
            parts.length === 5 &&
            parts[1] === 'G3DSA' &&
            parts[3] === 'FF'
          ) {
            const superfamily = parts[2]
            const funfam = String(Number(parts[4]))
            return `<a href="https://www.cathdb.info/version/v4_4_0/superfamily/${superfamily}/funfam/${funfam}" target="_blank">${dbxref}</a>`
          } else {
            return dbxref
          }
        } else if (dbxref.startsWith('Gene3D:')) {
          const ref = dbxref.replace('Gene3D:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/cathgene3d/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('Hamap:')) {
          const ref = dbxref.replace('Hamap:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/hamap/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('PANTHER:')) {
          const ref = dbxref.replace('PANTHER:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/panther/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('Pfam:')) {
          const ref = dbxref.replace('Pfam:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/pfam/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('PIRSF:')) {
          const ref = dbxref.replace('PIRSF:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/pirsf/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('PRINTS:')) {
          const ref = dbxref.replace('PRINTS:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/prints/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('ProSitePatterns:')) {
          const ref = dbxref.replace('ProSitePatterns:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/prosite/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('ProSiteProfiles:')) {
          const ref = dbxref.replace('ProSiteProfiles:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/profile/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SFLD:')) {
          const ref = dbxref.replace('SFLD:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/sfld/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SMART:')) {
          const ref = dbxref.replace('SMART:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/smart/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SUPERFAMILY:')) {
          const ref = dbxref.replace('SUPERFAMILY:', '')
          return `<a href="https://www.ebi.ac.uk/interpro/entry/ssf/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('TIGRFAM:')) {
          const ref = dbxref.replace('TIGRFAM:', '')
          return `<a href="https://tigrfams.jcvi.org/cgi-bin/HmmReportPage.cgi?acc=${ref}" target="_blank">${dbxref}</a>`
        }
        // Default: return plaintext if no link is defined
        return dbxref
      }).join('<br>')
    })

    pluginManager.jexl.addFunction('ontologyLinkout', feature => {
      if (!feature.ontology_term) {
        return ''
      }

      const goTerms = Array.isArray(feature.ontology_term) ? feature.ontology_term : [feature.ontology_term]

      return goTerms.map(ontology_term => {
        const ref = ontology_term.replace('GO:', '')
        if (ref === '-') {
          return ref
        }
        return `<a href="https://amigo.geneontology.org/amigo/term/GO:${ref}" target="_blank">${ontology_term}</a>`
      }).join('<br>')
    })

    pluginManager.jexl.addFunction('uniprotLinkout', feature => {
      if (!feature.uniprot_id) {
        return ''
      }

      const goTerms = Array.isArray(feature.uniprot_id) ? feature.uniprot_id : [feature.uniprot_id]

      return goTerms.map(uniprot_id => {
        return `<a href="https://www.uniprot.org/uniprotkb/${uniprot_id}" target="_blank">${uniprot_id}</a>`
      }).join('<br>')
    })
  }
}