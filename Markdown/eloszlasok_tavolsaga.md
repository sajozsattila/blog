

<span id="article_title">

Eloszlások távolsága

</span>


<span id="article_abstract">

A mai bejegyzésben több Statisztikai alakkérdést fogunk körbejárni: mit jelent hogy két eloszlás különbözik egymástól? Hogy számszerűsíthetjük a különbséget? Miként lehet ezt paraméterbecslésre használni? A bejegyzés végére a relatív entrópián keresztül el fogunk jutni a *likelihood* fogalmáig.  

</span>


Kezdjük egy alapkérdéssel: Mit csinálunk amikor paraméterbecslést végzünk? Lényegében van egy populációnk, aminek ismerjük az eloszlástípusát, de nem ismerjük az adott eloszlás konkrét paramétereit. Például van egy binális elemeket tartalmazó populációnk, ami ugye egy Bernoulli eloszlás. De nem ismerjük, hogy mekkora valószínűséggel lesz 1 az eredmény, vagyis, hogy mi a *p* konkrét értéke. A paraméterbecslés célja, hogy ezt a konkrét értéket meghatározzuk.

A blogon már többször volt erről a problémáról szó, de eddig nem jártuk körül az alapokat. Ezzel a témával kapcsolatban sok triviális állításról is beszélnünk kell, és nem éreztem annyira fontosnak eddig, hogy ezeket részletezem. Ez a helyzet annyiban változott meg, hogy készül egy bejegyzés a M becslésről, és annak megértéséhez talán nem árt részletesebben ismerni az alapokat.

Paraméterbecslés során van két eloszlásunk: a valós és az általunk becsült. Nem meglepő módon ha a becslésünk jó, akkor ez a kettő hasonlít egymáshoz.  Vagyis ha valós populációs paraméter, jelöljük $$\theta^{*}$$-al, mondjuk 0,2.  Akkor a 0,1 jobb becslés; jelöljük $$\theta$$-val; mint a 0,5, lévén az első közelebb van a valós értékhez.

# Total Variation Distance 

Ha a fentiekig eljutottunk, akkor nem túl nagy erőfeszítéssel  eljutunk annak felismerésig, hogy szükségünk van egy eljárásra, amivel mérni tudjuk a valós és becsült eloszlás távolságát.  Egy kis gondolkozás után a következő ábrához fogunk eljutni:

![1. ábra: Két sürüségfüggvény különbsége](https://sajozsattilahome.files.wordpress.com/2020/12/img_0667.png){#img:1} 

A fenti két folytonos függvény különbsége a narancssárgával besatírozott rész.  Gondolom mindenki látja miért. Ha a fenti ábra megvan, akkor számszerűsítsük őket. Ugye azt látjuk, hogy teljesen mindegy, hogy pozitív vagy negatív irányba tér el egymástól a két függvény. A különbség abszolút értéke számít nekünk.  Vagyis ezt keressük:

$$ | f_{\theta}(A) - f_{\theta^{*}}(A) | $${#eq:1} 

Ahol:
  + $$\theta$$ -- becsült paraméterünk
  + $$\theta^{*}$$ -- a valós paraméter
  + $$f_{\theta}(A)$$ -- a becsült függvényünk
  + $$f_{\theta^{*}}(A)$$ -- a valós függvény

Különböztessünk meg két esetet: Az első, amikor a becsült függvényünk nagyobb mint a valós^[A fenti ábrán ez az, amikor a zöld függvény értéke nagyobb mint a kék függvényé.], a másik amikor kisebb. 

Most részletezzük egy kicsit ez első esetet, vagyis amikor $$ f_{\theta}(X) \ge f_{\theta*}(X)$$:

$$  f_{\theta}(A) -  f_{\theta^{*}}(A) =  \int_{ p_{\theta}(X) \ge f_{\theta^{*}}(X) }   f_{\theta}(x) -  f_{\theta'}(x)  $$


Ahol:
  + $$f_{\theta}(x)$$ -- annak valószínűsége, hogy *x* értéket vesz fel a *becsült* paraméterünk
  + $$f_{\theta^{*}}(x)$$ -- annak valószínűsége, hogy *x* értéket vesz fel a *valós* paraméterünk
 + *A* -- azok az *x* értékek, amikre ebben az esetben igaz, hogy a becsült paraméterünk alapján számol a függvény a valós sűrűségfüggvénynél nagyobb. Vagyis: $$ A = \{ x\in E; f_{\theta}(x) \ge f_{\theta*}(x) \} $$
  + $$f_{\theta}(A)$$ -- a becsült függvényünk összesített valószínűsége, az A tartományban
  + $$f_{\theta^{*}}(A)$$ -- a valós függvényünk összesített valószínűsége, az A tartományban

Vegyük észre, hogy itt csak pozitív számok jöhetnek szóba, mivel kikötöttük, hogy $$ f_{\theta}(A) \ge f_{\theta^{*}}(A)$$. Egy pozitív szám abszolút értéke pedig önmaga, tehát a fenti így is felírható:

$$ | f_{\theta}(A) -  f_{\theta^{*}}(A) | =  \int_{ f_{\theta}(X) \ge f_{\theta^{*}}(X) }  | f_{\theta}(x) -  f_{\theta^{*}}(x) | $${#eq:2}

Ha ez megvan, nézzük meg a  komplementer halmazt, vagyis amikor a becsült függvényünk a valós függvénynél kisebb, tehát amikor $$ f_{\theta}(A) < f_{\theta^{*}}(A)$$ :

$$  f_{\theta}(A^c) -  f_{\theta^{*}}(A^c) =  \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }   f_{\theta}(x) -  f_{\theta^{*}}(x)  $$

Mivel azt tudjuk, hogy a két halmaz összege egy,^[Lévén ez a teljes valószínűség.] ezt felírhatjuk így:

$$  1-f_{\theta}(A) - 1 + f_{\theta^{*}}(A) =  \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }   f_{\theta}(x) -  f_{\theta^{*}}(x)  $$

Egyszerűsítsünk a bal oldalon:

$$  f_{\theta^{*}}(A)-f_{\theta}(A) =  \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }   f_{\theta}(x) -  f_{\theta^{*}}(x)  $$

Most nézzük a jobb oldalt.  Itt mindig negatív szám lesz,mivel kikötöttük, hogy  $$ P_{\theta}(A) < P_{\theta^{*}}(A)$$. Ennek megfelelően az abszolút értéküket -1-el szorozva visszakapjuk őket:

$$  f_{\theta^{*}}(A)-f_{\theta}(A) = - \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }  | f_{\theta}(x) -  f_{\theta^{*}}(x) | $$

A bal oldalra is igaz ugyanez:

$$ - | f_{\theta^{*}}(A)-f_{\theta}(A) | = - \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }  | f_{\theta}(x) -  f_{\theta^{*}}(x) | $$

Negatív kiesik:

$$  | f_{\theta^{*}}(A)-f_{\theta}(A) | = \int_{ f_{\theta}(X) < f_{\theta^{*}}(X) }  | f_{\theta}(x) -  f_{\theta^{*}}(x) | $${#eq:3}

Ha most összeadjuk a [(2)](#eq:2) és a [(3)](#eq:3)-t, akkor megkapjuk a két függvény teljese távolságát:^[Ugye  $$  f_{\theta}(X) \ge f_{\theta^{*}}(X) $$ és a $$  f_{\theta}(X) < f_{\theta^{*}}(X) $$ eseteke összege egyenlő $$ x\in E $$ ]

$$  | f_{\theta}(A) -  f_{\theta^{*}}(A) | + | f_{\theta^{*}}(A)-f_{\theta}(A) | = \int_{x\in E}  | f_{\theta}(x) -  f_{\theta^{*}}(x) | $$

Az abszolut érték miatt a jobb oldalon az elemek sorrendje felcserélhető, vagyis:

$$ 2 \cdot  | f_{\theta}(A) -  f_{\theta^{*}}(A) | = \int_{x\in E}  \left| f_{\theta}(x) -  f_{\theta^{*}}(x) \right| $$

Osszunk kettővel és meg is kapjuk a két függvény távolságát:

$$ | f_{\theta}(A) -  f_{\theta^{*}}(A) | = \frac{1}{2}  \int_{x\in E}  \left| f_{\theta}(x) -  f_{\theta*}(x) \right| $${#eq:4}

Diszkrét eloszlásra is elkészíthetjük ugyanezt:

$$ | P_{\theta}(A) -  P_{\theta^{*}}(A) | = \frac{1}{2}  \sum_{x\in E}  \left| f_{\theta}(x) -  f_{\theta*}(x) \right| $${#eq:5}

Az fenti különbségnek neve is van: Total Variation Distance^[Tud erre valaki valami jó magyarítást?], szokás TV-vel jelölni.


# Kullback--Leibler-divergencia^[Nevezik még Relatív entrópiának is.]

Rendben, de mivel is vagyunk előrébb a fenti gyakorlattal? Ez dob nekünk egy számot, amivel le tudjuk írni két sürüségfüggvény távolságát. Értelemszerűen minél kisebb ez a szám, annál jobb a becslésünk.  Vagyis a TV segítségével minimalizációs problémaként tudjuk megközelíteni a paraméterbecslést.

Tegyük ezt meg, és ábrázoljuk a Total Variation Distance-t és a $$\theta$$-t közös grafikonon:

![2.ábra: Eloszlások távolsága vs. paraméterbecslés ](https://sajozsattilahome.files.wordpress.com/2020/12/img_0668.png){#img:2}


A fenti ábrán nincs semmi meglepő. Érteleszerűen minél távolabb van $$\theta$$ a $$\theta^{*}$$-tól annál nagyobb a TV.  Persze van itt egy probléma. Ahhoz, hogy Total Variation Distance-t számoljunk, ismernünk kell a valós  $$\theta^{*}$$.  Dehát, pont ez az ismeretlen, amit keresünk! Kicsit 22-es csapdája. Szerencsére ismerjük a nagy számok törvényét. Ami azt mondja ki: ahogy egyre több mintánk van a minta átlaga egyre közelebb kerül a valós populáció átlaghoz. Miért jó ez? Mi lenne, ha a  $$\theta^{*}$$ helyére behelyettesítenénk a átlagot?  Ekkor kapnánk egy eljárást, amiről tudjuk, hogy ahogy nő a mintaszám egyre közelebb kerül a valós átlaghoz, ami ebben az esetben a  $$\theta^{*}$$. A Kullback--Leibler-divergencia ezt csinálja.  Úgy méri két eloszlás távolságát, hogy felhasználja a mintaátlagot hozzá.

In medias res, nézzük, hogy kell kiszámolni:

$$ \text{KL}(P_{\theta}, P_{\theta^{*}})  = \sum _{x \in E} p_{\theta}(x) \cdot \ln \left[ \frac{p_{\theta}(x)}{p_{\theta^{*}}(x)} \right] $${#eq:6}

$$ \text{KL}(P_{\theta}, P_{\theta^{*}})  = \int _{x \in E} f_{\theta}(x) \cdot \ln \left[ \frac{f_{\theta}(x)}{f_{\theta^{*}}(x)} \right] \text{dx} $${#eq:7}


Ha a KL és a $$\theta$$-t ábrázolása a [2. ábrához](#img:2) nagyon hasonló lenne. A függőleges értékek számszerűen mások lennének, de a görbe alakja ugyanaz maradna. És erre is igaz, hogy a valós $$\theta^{*}$$-ban éri el a KL a minimumát. 

Ok, de hol van itt az átlag? A [(7)]({#eq:7}) egyenlet így is felírható:

$$ \text{KL}(P_{\theta}, P_{\theta^{*}}) = E[\theta^{*}] \cdot \left[ \ln \frac{p_{\theta^{*}}(x)}{p_{\theta}(x)} \right] $$

Ahol:
 + $$ E[\theta^{*}]$$ -- az elvárt érték a $$\theta$$-ra, lényegében a paraméterbecslésünk.

Ha ezt egy kicsit továbbvisszük el fogunk érkezni a statisztika legelterjedtebb paraméterbecslési eljárásához. Tegyük ezt meg. Az átlagok lineárisak, tehát $$ E(X)-E(Y) = E(X-Y) $$, felhasználva ezt és a logaritmust:

$$ \text{KL}(P_{\theta}, P_{\theta^{*}}) = E[\theta^{*}] \cdot \left[ \ln p_{\theta^{*}}(X)\right] - E[\theta^{*}] \cdot \left[ \ln p_{\theta}(X) \right] $$

Vegyük észre, hogy az jobb oldal első felét nem ismerjük, ami ez egy konstans, és csak a valós paramétertől függ. Jelöljük ezt az ismeretet:

$$ \text{KL}(P_{\theta}, P_{\theta^{*}}) = K - E[\theta^{*}] \cdot \left[ \ln p_{\theta}(X) \right] $$

A fenti konstanson kívül csak a paraméterbecslés elvárt étekét nem ismerjük a jobb oldalon.^[Igazából a *p*-t se ismerjük feltétlenül.  De általában a problémából következtethetünk arra, hogy milyen eloszlást követ a populáció. Így az esetek többségében tekinthetjük ismertnek. Ha nem, akkor elhagyjuk a statisztika területét és a gépi tanulás vizeire vitorlázunk.] Ez mint korábban eldöntöttük a populáció átlaga lesz.  Így segítségül hívhatjuk a nagy számok törvényét. Megtehetjük, hogy egyszerűen behelyettesítjük a mintaátlaggal, mivel sok minta estén a kettő nagyon közel van egymáshoz:


$$ \text{KL}(P_{\theta}, P_{\theta^{*}}) = K - \frac{1}{n}\sum_{i=1}^n \log p_{\theta}(x_i) $$

Emlékeztet ez valamire? A Maximum Likelihood számításra? Hogy egyértelmű legyen ez a hasonlóság idézzük fel mi a célunk: a megbecsült paraméter minél közelebb legyen a valós paraméterhez. Vagyis, hogy minimalizáljuk a Kullback--Leibler-divergenciát.  Vegyük észre, hogy a minimalizáció szempontjából a konstans nem számít. Tehát:

$$ min( \text{KL}(P_{\theta}, P_{\theta^{*}}) ) \Leftrightarrow min\left( - \frac{1}{n}\sum_{i=1}^n \log p_{\theta}(x_i)\right) $$


Most dolgozzunk ezen egy kicsit. Minimalizáció és a maximalizáció lényegében ugyanaz a probléma csak $$ -1 $$-el szorozva. Ennek segítségével eltüntetjük a jobb oldal mínusz jelét:


$$ min( \text{KL}(P_{\theta}, P_{\theta^{*}}) ) \Leftrightarrow max\left(  \frac{1}{n}\sum_{i=1}^n \log p_{\theta}(x_i)\right) $$

Kicsit rendezzük át:

$$ min( \text{KL}(P_{\theta}, P_{\theta^{*}}) ) \Leftrightarrow max\left( \log \prod_{i=1}^n  p_{\theta}(x_i)\right) $$

Voilà, itt is van a log maximum likelihood principle. Persze el is távolíthatjuk a logaritmust. És akkor megérkeztünk a *likelihood*-hoz:

$$ \text{likelihood} = \prod_{i=1}^n  p_{\theta} (x_i) $${#eq:8}

Mi is ez? Nem más mint, hogy a *megfigyelt adatunk mekkora valószínűséggel származik a $$\theta$$ paraméterű eloszlásból*.^[Persze ennek eredménye nem 0 és 1 közötti, mert hiányzik a normalizációs faktor: a Teljes valószínűség tétele.  Így meg is érkeztünk a Bayes tételhez nagyjából.]  Ennek a maximuma meg az a paraméter, ami legnagyobb valószínűséggel magyarázza a megfigyelést.  Ami logikusan az a paraméter is ahol a legkisebb a valós paraméter és a becslésünk távolsága. 

#### Rekrám
A bejegyzés az ingyenes valós idejű közös munkát támogató online [μr² Markdown szerkesztővel](https://mur2.co.uk/editor) készült. 
