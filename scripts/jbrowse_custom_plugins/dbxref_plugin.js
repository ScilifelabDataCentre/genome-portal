export default class DbxrefPlugin {
  name = 'SRGP-DbxrefPlugin'
  version = '1.0.0'

  install() {}

  configure(pluginManager) {
    pluginManager.jexl.addFunction('linkout', feature => {
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
        } else if (dbxref.startsWith('Pfam:')) {
          const ref = dbxref.replace('Pfam:', '')
          return `<a href="https://pfam.xfam.org/family/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('ProSiteProfiles:')) {
          const ref = dbxref.replace('ProSiteProfiles:', '')
          return `<a href="https://prosite.expasy.org/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('ProSitePatterns:')) {
          const ref = dbxref.replace('ProSitePatterns:', '')
          return `<a href="https://prosite.expasy.org/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SMART:')) {
          const ref = dbxref.replace('SMART:', '')
          return `<a href="https://smart.embl.de/smart/do_annotation.pl?DOMAIN=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('Gene3D:')) {
          const ref = dbxref.replace('Gene3D:', '')
          return `<a href="http://www.cathdb.info/version/latest/superfamily/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SUPERFAMILY:')) {
          const ref = dbxref.replace('SUPERFAMILY:', '')
          return `<a href="https://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('PANTHER:')) {
          const ref = dbxref.replace('PANTHER:', '')
          return `<a href="http://www.pantherdb.org/panther/family.do?clsAccession=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('PRINTS:')) {
          const ref = dbxref.replace('PRINTS:', '')
          return `<a href="https://www.bioinf.manchester.ac.uk/cgi-bin/dbbrowser/PRINTS/DoGET.pl?ac=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('TIGRFAMs:')) {
          const ref = dbxref.replace('TIGRFAMs:', '')
          return `<a href="https://tigrfams.jcvi.org/cgi-bin/HmmReportPage.cgi?acc=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('CDD:')) {
          const ref = dbxref.replace('CDD:', '')
          return `<a href="https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('SFLD:')) {
          const ref = dbxref.replace('SFLD:', '')
          return `<a href="https://sfld.rbvi.ucsf.edu/django/ontology/family/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('MobiDBLite:')) {
          const ref = dbxref.replace('MobiDBLite:', '')
          return `<a href="https://mobidb.bio.unipd.it/entries/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('FunFam:')) {
          const ref = dbxref.replace('FunFam:', '')
          return `<a href="http://www.cathdb.info/version/latest/superfamily/${ref}" target="_blank">${dbxref}</a>`
        } else if (dbxref.startsWith('Coils:')) {
          // Coils does not have a direct URL, return plaintext
          return dbxref
        }

        // Default: return plaintext if no link is defined
        return dbxref
      }).join('<br>')
    })
  }
}