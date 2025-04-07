import os
import logging
from collector import verzamel_systeeminfo, gebruikers_info, geinstalleerde_software, actieve_processen, netwerk_config, usb_info, recente_bestanden, browsergeschiedenis,geinstalleerde_remote_tools    

# Log configuratie
logging.basicConfig(level=logging.INFO)

def logbestand_legen(bestandsnaam):
    """Leeg het logbestand als het bestaat."""
    if os.path.exists(bestandsnaam):
        os.remove(bestandsnaam)
        logging.info(f"Logbestand {bestandsnaam} is geleegd.")

def schrijf_naar_log(bestandsnaam, titel, data):
    with open(bestandsnaam, "a") as f:
        f.write(f"\n=== {titel} ===\n")
        
        # Voeg de lijst als complete regels toe
        if isinstance(data, list):
            f.write("\n".join(data))  # Voeg de items in de lijst samen zonder extra nieuwe regels
            f.write("\n")  # Voeg één extra nieuwe regel na de lijst toe
        else:
            f.write(f"{data}\n")

def main():
    """Hoofd functie die systeeminformatie verzamelt en naar een logbestand schrijft."""
    
    logbestand = "output_log.txt"
    
    # Leeg het logbestand bij elke draai
    logbestand_legen(logbestand)
    
    # Verzamel informatie
    systeeminfo = verzamel_systeeminfo()
    gebruikersinfo = gebruikers_info()
    software_info = geinstalleerde_software()
    actieve_processen_info = actieve_processen()
    netwerk_info = netwerk_config()
    usb_info_data = usb_info()
    recente_bestanden_info = recente_bestanden()
    browser_geschiedenis_info = browsergeschiedenis()
    remote_tools_info = geinstalleerde_remote_tools()

    # Schrijf de verzamelde informatie naar het logbestand
    schrijf_naar_log(logbestand, "Systeeminformatie", systeeminfo)
    schrijf_naar_log(logbestand, "Gebruikersinformatie", gebruikersinfo)
    schrijf_naar_log(logbestand, "Geïnstalleerde Software", software_info)
    schrijf_naar_log(logbestand, "Actieve Processen", actieve_processen_info)
    schrijf_naar_log(logbestand, "Netwerkconfiguratie", netwerk_info)
    schrijf_naar_log(logbestand, "USB-informatie", usb_info_data)
    schrijf_naar_log(logbestand, "Recente Bestanden", recente_bestanden_info)
    schrijf_naar_log(logbestand, "Browsergeschiedenis", browser_geschiedenis_info)
    schrijf_naar_log(logbestand, "Geïnstalleerde Remote Tools", remote_tools_info)

    logging.info("Alle informatie is verzameld en opgeslagen in output_log.txt")

if __name__ == "__main__":
    main()