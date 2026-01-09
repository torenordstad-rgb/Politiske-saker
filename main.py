import asyncio
from playwright.async_api import async_playwright

# Nøkkelord definert ut fra satsingsområdene i "Klimaløftene"
KLIMALOFTENE = {
    "Natur og arealbruk": ["areal", "natur", "skog", "jordvern", "fortetting", "grønnstruktur"],
    "Energi og effekt": ["enøk", "energi", "solcelle", "strøm", "fjernvarme", "effekt"],
    "Mobilitet og transport": ["sykkel", "buss", "transport", "mobilitet", "bil", "parkering"],
    "Bygg og anlegg": ["ombruk", "bygg", "anlegg", "materialvalg", "klimagassregnskap"],
    "Forbruk og avfall": ["avfall", "sirkulær", "gjenbruk", "forbruk", "kildesortering"],
    "Karbonopptak": ["ccs", "karbonfangst", "treplanting", "biokull"],
    "Klimatilpasning": ["overvann", "flom", "klimasårbarhet", "ekstremvær"],
    "Rettferdig omstilling": ["folkehelse", "sosial", "fordeling", "demokrati"],
    "Næring og arbeid": ["næring", "innovasjon", "grønn vekst", "arbeidsplasser"]
}

async def hent_politiske_saker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Gå til Trondheim kommunes møtekalender
        url = "https://trondheim-elements.digdem.no/motekalender"
        print(f"Åpner {url}...")
        await page.goto(url, wait_until="networkidle")

        # Vent på at sakene lastes inn (vi ser etter lenker eller rader i kalenderen)
        # Dette selektoren må ofte justeres basert på Elements sin spesifikke struktur
        await page.wait_for_selector(".meeting-item, .agenda-item", timeout=10000)
        
        saker = await page.query_selector_all(".agenda-item-title") # Eksempel på klasse
        
        print(f"Fant {len(saker)} saker. Analyserer mot Klimaløftene...\n")
        
        treff_liste = []

        for sak in saker:
            tittel = await sak.inner_text()
            relevant_for = []
            
            for lofte, keywords in KLIMALOFTENE.items():
                if any(k.lower() in tittel.lower() for k in keywords):
                    relevant_for.append(lofte)
            
            if relevant_for:
                treff_liste.append({
                    "tittel": tittel.strip(),
                    "kategorier": ", ".join(relevant_for)
                })

        await browser.close()
        return treff_liste

# Kjør skanneren
if __name__ == "__main__":
    resultat = asyncio.run(hent_politiske_saker())
    
    if resultat:
        print(f"{'SAKSTITTEL':<60} | {'RELEVANT KLIMALØFTE'}")
        print("-" * 90)
        for sak in resultat:
            print(f"{sak['tittel'][:58]:<60} | {sak['kategorier']}")
    else:
        print("Ingen direkte treff på nøkkelord i dagens liste.")
