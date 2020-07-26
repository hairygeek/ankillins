Generates Anki cards from Collins pages.
# ankillins
Ankillins is a Command Line Application that generates Anki cards from collinsdictionary.com pages.
![generated card example](https://i.imgur.com/dDps8GU.png)
## Features 
* Generating cloze card for every definition
* Word pronounce in cards 
* Examples pronounce support (locked because of high memory usage)
* Words search support
* Original site styles
## Usage
```shell script
➜ ankillins search "At the end of the day"
at the end of the day
➜ ankillins gen-cards "At the end of the day"
Word "At the end of the day" processed successfully
➜ ankillins gen-cards hello knife spider "so on" kek does_not_exists "sort of" kind
Word "hello" processed successfully
Word "knife" processed successfully
Word "spider" processed successfully
Word "so on" processed successfully
[Error] Word kek not found
Similar words: keck, keek, keks, kike, eek, kak, keV, kea, keb, ked, kef, keg, ken, kep, ket, kex, key, lek, nek, zek
[Error] Word does_not_exists not found
Similar words: dentists, kenoticists
Word "sort of" processed successfully
Word "kind" processed successfully
➜ ls -lh
total 32K
-rw-r--r-- 1 hairygeek hairygeek 31K Jul 26 12:56 ankillins-result.csv
```
Ankillins doesn't add cards to Anki itself. Instead, it generates `ankillins-result.csv` file which you need to import. 
### Important details
* When you import result file click on the "fields separated by" and type `~`
* It is better to create your own card type with styles located in `card_styles.css` to get card style close to collinsdictionary page style.

## Installation
*Will be available sooner*

