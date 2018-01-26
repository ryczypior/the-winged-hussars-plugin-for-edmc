# Wtyczka The Winged Hussars do aplikacji Elite: Dangerous Market Connector (EDMC)

To jest wtyczka dla [EDMC](https://github.com/Marginal/EDMarketConnector) napisana w Pythonie, która umożliwia członkom [TWH](http://thewingedhussars.com/) wysyłanie danych z logu dzinnika gry [Elite: Dangerous](https://www.elitedangerous.com/) do API aplikacji BGS. **TA WTYCZKA PRZEZNACZONA JEST TYLKO DLA HUSARZY Z FORUM THE WINGED HUSSARS! MUSISZ POSIADAĆ KONTO NA FORUM TWH PRZYNAJMNIEJ W RANDZE HUSARZA, BY KORZYSTAĆ Z TEJ WTYCZKI!**


## Wymagania

* Musisz posiadać konto w randze Husarza lub wyższej na forum The Winged Hussars i musisz posiadać wygenerowany klucz API do wtyczki
* Musisz mieć zainstalowaną aplikację [EDMC](https://github.com/Marginal/EDMarketConnector)

## Instalacja

* Pobierz [najnowszą wersję pluginu](https://github.com/ryczypior/the-winged-hussars-plugin-for-edmc/releases/download/1.11/twh.zip)
* Wypakuj pobrany plik (archiwum ZIP) do folderu wtyczek EDMC:
    - dla MS Windows: %LOCALAPPDATA%\EDMarketConnector\plugins (np. C:\Users\YOURWINDOWSACCOUNT\AppData\Local\EDMarketConnector\plugins\)
    - dla MAC: ~/Library/Application Support/EDMarketConnector/plugins/
* Powinny być widoczne pliki %LOCALAPPDATA%\EDMarketConnector\plugins\twh\load.py dla MS Windows lub ~/Library/Application Support/EDMarketConnector/plugins/twh/load.py dla MAC
* Po uruchomieniu EDMC należy przejść do ustawień i w karcie TWH wpisać swoją nazwę użytkownika oraz wygenerowany klucz API
* Po zapisaniu tych informacji w oknie programu EDMC powinna pojawić się informacja - aktualny czas i dopisek "Online"