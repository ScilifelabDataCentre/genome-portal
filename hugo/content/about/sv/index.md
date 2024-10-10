---
title: Information på svenska
---

## Översikt

The Swedish Reference Genome Portal ("Den svenska portalen för referens-genom") är en kostnadsfri tjänst som syftar till att samla, tillgängliggöra och visualisera genom-assemblies och -annoteringar från icke-humana eukaryota arter producerade av eller i samarbete med forskare med an­knytning till institutioner i Sverige. Denna tjänst tillhandahålls och underhålls av *The Data Science Node in Evolution and Biodiversity (DSN-EB)* som består av ett team av data stewards, dataingenjörer, systemutvecklare och bioinformatiker från [National Bioinformatics Infrastructure Sweden (NBIS)](https://nbis.se) och [SciLifeLab Data Centre](https://www.scilifelab.se/data/).

Arbetet med portalen är finansierat av [SciLifeLab](https://www.scilifelab.se) och [Knut and Alice Wallenbergs Stiftelse](https://kaw.wallenberg.org/) genom det nationella programmet för [Data-Driven Life Science (DDLS)](https://www.scilifelab.se/data-driven/), samt av [Stiftelsen för Strategisk Forskning (SSF)](https://strategiska.se/).

**The Swedish Reference Genome Portal syftar till att:**

- framhäva och visa upp forskning om icke-humana eukaryota genom som utförts i Sverige.
- främja offentlig delning av typer av genomik-data som annars sällan publiceras.
- säkerställa att all data som visas upp i genomportalen är i linje med [FAIR-principerna](https://www.go-fair.org/fair-principles/) och tillgängliga i offentliga repositorier.
- underlätta åtkomst, visualisering och tolkning av genomdata.

## Användning

Alla är välkomna att använda denna webbplats, men för att kunna skicka in ett dataset till genomportalen finns det några få krav. Läs mer om kraven här: [requirements for adding a genome project](/contribute) (på engelska).

## Tekniska detaljer

Denna webbsida är byggd med hjälp av [Hugo](https://gohugo.io/) som är ett verktyg för att skapa statiska webbsidor. Genombrowsern [JBrowse2](https://jbrowse.org/jb2/)  används för att visualisera genomik-datan och är inbäddad i den statiska webbsidan. All data i genomportalen är öppet tillgänglig via offentliga repositorier. Portalen hämtar en kopia av all data för att visa upp i genombrowsern.

Genomportalen använder sig av öppen källkod under en *MIT open source*-licens. Källkoden  finns att tillgå på [GitHub](https://github.com/ScilifelabDataCentre/genome-portal/). Portalen är driftsatt på ett [Kubernetes](https://kubernetes.io/)-kluster som finns vid  [Kungliga Tekniska Högskolan (KTH)](https://www.kth.se/) i Stockholm.
