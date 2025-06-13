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

      
    function makeATag(href, text) {
      return `<a href="${href}" target="_blank">${text}</a>`;
    }

    pluginManager.jexl.addFunction('dbxrefLinkout', feature => {
      if (!feature.dbxref) {
        return ''
      }

      const dbxrefs = Array.isArray(feature.dbxref)
        ? feature.dbxref
        : [feature.dbxref]
      
      const dbxrefMap = {
        'InterPro:': ref => `https://www.ebi.ac.uk/interpro/entry/${ref}`,
        'CDD:': ref => `https://www.ebi.ac.uk/interpro/entry/cdd/${ref}`,
        'Gene3D:': ref => `https://www.ebi.ac.uk/interpro/entry/cathgene3d/${ref}`,
        'Hamap:': ref => `https://www.ebi.ac.uk/interpro/entry/hamap/${ref}`,
        'PANTHER:': ref => `https://www.ebi.ac.uk/interpro/entry/panther/${ref}`,
        'Pfam:': ref => `https://www.ebi.ac.uk/interpro/entry/pfam/${ref}`,
        'PIRSF:': ref => `https://www.ebi.ac.uk/interpro/entry/pirsf/${ref}`,
        'PRINTS:': ref => `https://www.ebi.ac.uk/interpro/entry/prints/${ref}`,
        'ProSitePatterns:': ref => `https://www.ebi.ac.uk/interpro/entry/prosite/${ref}`,
        'ProSiteProfiles:': ref => `https://www.ebi.ac.uk/interpro/entry/profile/${ref}`,
        'SFLD:': ref => `https://www.ebi.ac.uk/interpro/entry/sfld/${ref}`,
        'SMART:': ref => `https://www.ebi.ac.uk/interpro/entry/smart/${ref}`,
        'SUPERFAMILY:': ref => `https://www.ebi.ac.uk/interpro/entry/ssf/${ref}`,
        'TIGRFAM:': ref => `https://tigrfams.jcvi.org/cgi-bin/HmmReportPage.cgi?acc=${ref}`,
        'Reactome:': ref => `https://reactome.org/content/detail/${ref}`,
        'AntiFam:': ref => `https://www.ebi.ac.uk/interpro/entry/antifam/${ref}`,
        'MetaCyc:': ref => `https://metacyc.org/pathway?orgid=META&id=${ref}`,
      }


      return dbxrefs.map(dbxref => {
        let url = '';

        if (dbxref.startsWith('FunFam:')) {
          const parts = dbxref.split(':');
          if (parts.length === 5 && parts[1] === 'G3DSA' && parts[3] === 'FF') {
            const superfamily = parts[2];
            const funfam = String(Number(parts[4]));
            url = `https://www.cathdb.info/version/v4_4_0/superfamily/${superfamily}/funfam/${funfam}`;
          }
        }

        if (!url && dbxref.startsWith('KEGG:')) {
          const keggRef = dbxref.replace('KEGG:', '');
          const pathwayId = keggRef.split('+')[0];
          url = `https://www.genome.jp/entry/map${pathwayId}`;
        }

        if (!url) {
          for (const [prefix, urlMaker] of Object.entries(dbxrefMap)) {
            if (dbxref.startsWith(prefix)) {
              const ref = dbxref.replace(prefix, '');
              url = urlMaker(ref);
              break;
            }
          }
        }

        if (url) {
          return makeATag(url, dbxref);
        } else {
          return dbxref;
        }
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
        return makeATag(`https://amigo.geneontology.org/amigo/term/GO:${ref}`, ontology_term);
      }).join('<br>')
    })

    pluginManager.jexl.addFunction('uniprotLinkout', feature => {
      if (!feature.uniprot_id) {
        return ''
      }

      const goTerms = Array.isArray(feature.uniprot_id) ? feature.uniprot_id : [feature.uniprot_id]

      return goTerms.map(uniprot_id => {
        return makeATag(`https://www.uniprot.org/uniprotkb/${uniprot_id}`, uniprot_id);
      }).join('<br>')
    })
  }
}