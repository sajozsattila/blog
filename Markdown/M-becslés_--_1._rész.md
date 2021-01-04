<span id="article_title">
M-becslés -- 1. rész</span>

<span id="article_abstract">Az [M estimator](https://en.wikipedia.org/wiki/M-estimato) lényegében a [maximum likelihood becslés](https://sajozsattila.home.blog/2019/04/02/parameterbecsles-maximum-likelihood-modszerrel/) általánosításaként született meg az az 1960-as években [Peter J. Huber](https://en.wikipedia.org/wiki/Peter_J._Huber) nyomán. Amiért kifejezetten érdekes mert lehetőséget komoly előrelépést jelentett a robusztus statisztika irányába. Ebben a részben átnézzük az eljárás alapjait és egy egyszerűbb, de *nem robusztus* alkalmazását.
</span>



## Az alapötlet
Korábban már megismertük a [loss függvény](https://sajozsattila.home.blog/2019/04/03/statisztika-alapok-a-loss-fuggveny/) fogalmát.  Amikor ezt emlegetjük akkor igazából ezt gondoljuk: 

> Van egy függvényünk. Az eloszlásom *igazi* paramétere minimalizálja ezt a függvényt.  Tehát ha megtalálom ennek a függvénynek a minimumát akkor megvan az *igazi* paraméterem.

Van egy másik híres paraméter becslési eljárásunk is:  [Maximum Likelihood](https://sajozsattila.home.blog/tag/maximum-likelihood/). Ez lényegében a loss függvény ellentéte, tehát:

> Van egy függvényünk. Az eloszlásom *igazi* paramétere maximalizálja ezt a függvényt.  Tehát ha megtalálom ennek a függvénynek a maximumát, akkor megvan az *igazi* paraméterem.

Vegyük észre, hogy ez a kettő ugyanaz a probléma, ha -1-el megszorozzuk az egyiket, akkor a másikat fogjuk megkapni.

Az M becslést 1964-ben Peter J. Huber dolgozta ki és Maximum Likelihood általánosítása minimalizációs problémaként. Vagyis egyszerűen: 

> Paramétert szeretnél becsülni? Találj egy függvényt, aminek a minimumát, vagy maximumát az *igazi* paraméternél  veszi fel. 

Miért érdekes ez? A cél nem feltétlen a populáció valós eloszlásának a paraméterbecslése. Lényegében bármilyen tulajdonságot megcélozhatunk. Lehet például a medián, vagy a felső tíz százalék. Egy ilyen általános célhoz általános megfogalmazás is illik, ami jelen esetben:

$$ \widehat{\theta} = \arg\min_{\displaystyle\theta}\left(\sum_{i=1}^n\rho(x_i, \theta)\right)$${#eq:1}

Ahol:

+ $$\theta$$ -- a keresett populációs jellemző, pl: felső tíz százalék.
+ $$\widehat{\theta}$$ -- a becslésünk a populációs jellemzőre
+ $$x_i$$ -- a megfigyelés
+ *n* -- a mintavételek száma
+ $$\rho$$ -- pedig lényegében bármilyen függvény lehet, amire igaz, hogy ha minimalizáljuk, akkor a populációra jellemző igazi értékhez közelítünk. 

Mi ez? A Gépi tanulás alapötlete. Van egy függvényem, a *ró*, aminek két bemeneti értéke van. Az egyik a megfigyelésem, a másik az összes lehetséges érték, amit a paraméterem felvehet. A legjobb becslésünk pedig arra a paraméterre, amiből az adatok származnak az, ahol ez a *ró* függvény a minimum.


Gondolom már mindenkiben kezd érlelődni a kérdés: Rendben, de hogy a fenébe találjuk meg ezt a függvényt? Mit csinálunk, ha valaki bemondja nekünk, hogy találjuk meg a maximumát vagy a minimumát egy folytonos függvénynek?  Deriválunk. Akkor ez a válasz? Sajnos csak részben. Mivel egy nagyon általános eljárásról beszélünk nem minden esetben lehetséges a deriválás.  Ennek megfelelően az M-becslés két fajta altípusát különböztetjük meg: a *Pszi*-t (ψ), ami deriválható első fokon thétára  és a *ró*-t (ρ), ami pedig nem.^[Gondolom csak azért lett ez is ró, hogy növeljék a lehetséges hibák számát.] Amennyiben deriválható a *ró*, akkor igaz, hogy:

$$\mathbb E_F[\Psi(x_i, \theta)] = \int \Psi(x_i, \theta) dF(x) = 0 $$

Ahol:

+ $$ \mathbb E $$ -- elvárt érték, vagyis az átlag
+ $$F(x)$$ -- eloszlásfüggvénye 
+ $$\Psi(x_i, \theta)$$ -- az első fokon deriválható mágikus  függvényünk 

Ebben a részben csak ezeket az eseteket fogjuk részletezni. De először nézzük meg, mi jellemző az M-becslésre.

## Az M-becslés tulajdonságai

A legfontosabb tulajdonsága, hogy aszimptotikusan normális. Mit jelent ez? Annak a garanciáját: ahogy nő a mintavételek száma, a becsült paraméter és a valós paraméter közelit egymáshoz. Vagyis:

$$ \widehat{\theta}_n \xrightarrow [n \to \infty ]{P} \theta ^* $$

Mennyire bízhatunk meg a becsült paraméterértékben, vagyis mi a konfidencia intervallumunk? Akinek ismerős a [Centrális határeloszlás-tétele](https://sajozsattila.home.blog/2019/05/09/centralis-hatareloszlas-tetel-statisztika-lapok/), annak ez nem lesz meglepetés:

$$\sqrt{n} \frac{\widehat{\theta }_ n - \theta ^*}{\sqrt{ J(\theta ^*)^{-2} K(\theta ^*)} } \xrightarrow [n \to \infty ]{(d)} N(0,1) $${#eq:2}

Ahol:

 + $$N(0,1)$$ -- Egy standard normál eloszlás.
 + $$J(\theta ^*)$$ -- A *ró* [Hesse-mátrixának](https://hu.wikipedia.org/wiki/Hesse-m%C3%A1trix) elvárt értéke. Lásd lentebb.
 + $$K(\theta ^*)$$ --  A *ró* deriváltjának a varianciája. Lásd lentebb.

Ebből ugye ki lehet fejezni a konfidencia tartományt:

$$ \theta^* \in \left[ \widehat{\theta} - q_{\alpha} \cdot\frac{\sqrt{ J(\theta ^*)^{-2} \cdot K(\theta ^*)  } }{\sqrt{n}}, \widehat{\theta} + q_{\alpha} \cdot\frac{\sqrt{ J(\theta ^*)^{-2} \cdot K(\theta ^*)  } }{\sqrt{n}} \right] $${#eq:3}

Mik ezek a mágikus *J* és *K* értékek? A *J* a [Delta módszerből](http://sajozsattila.home.blog/tag/delta-modszer/) származik és a következő a definíciója:

$$ J(\theta ^*) =  \mathbb E[\mathbf{H}\rho ] =  \mathbb E\left[\begin{pmatrix} \frac{\partial ^2 \rho }{\partial \theta^* _1 \partial \theta^* _1} (\mathbf{X}_1, \vec{\theta })& \ldots &  \frac{\partial ^2 \rho }{\partial \theta^* _1 \partial \theta^*_ d} (\mathbf{X}_1, \vec{\theta })\\ \vdots & \ddots & \vdots \\ \frac{\partial ^2 \rho }{\partial \theta^*_ d \partial \theta^*_1} (\mathbf{X}_1, \vec{\theta^* })& \ldots &  \frac{\partial ^2 \rho }{\partial \theta^*_ d \partial \theta^*_ d} (\mathbf{X}_1, \vec{\theta^* })\end{pmatrix}\right]\qquad (d\times d)$$

A *K* pedig a *ró* deriváltjának varianciája:

$$ K(\theta ^*) = \text {Cov}\left[ \nabla \rho (X, \theta^* ) \right] $$

A *J* és a *K* egy paraméter esetén egyszerűen:

$$ J(\theta ^*) =  \mathbb E\left[ \frac{\partial ^2}{\partial \theta^* \partial \theta^*}  \rho (X, \theta^* ) \right]$$

$$  K(\theta ^*) = \text {Var}\left[ \frac{\partial }{\partial \theta^* }\rho (X, \theta^* ) \right] $$

Persze itt megint beleütközünk a szokásos problémába: a konfidencia intervallumunk a keresett $$\theta^*$$ értéktől függ. Amit nem ismerünk. A blog olvasói már tudják mit kell csinálni: [Slutsky](https://en.wikipedia.org/wiki/Slutsky%27s_theorem)-ra hivatkozva behelyettesítjük a megfigyelt adatokból számolt értéket. Ezt pont az M-becslés aszimptotikus normalitása miatt tehetjük meg.

A kezdeti bevezetés után talán egyértelmű, hogy a Maximum Likelihood az M-becslés egy speciális esete.  Ilyenkor a *J* és a *K* értéke egyenlő és megegyeznek a [Fisher információval](http://sajozsattila.home.blog/tag/fisher-informacio/). A konfidencia tartomány számítására ilyen esetben már láttunk példát a [Paraméterbecslés Maximum likelihood módszerrel](https://sajozsattila.home.blog/2019/04/02/parameterbecsles-maximum-likelihood-modszerrel/) bejegyzésben.


# Négyzetes hiba
A négyzetes hiba^[Angolul: Mean squared] egy tipikus loss függvény. Azért szeretjük, mert deriválható, és azért nem, mert egy kiugró érték nagyon képes elvinni, vagyis nem robosztus. Számítása:

$$ \rho(X, \theta^*) = (x-\theta)^2 $${#eq:4}


Mint fentebb már megjegyeztük, ez szerencsénkre deriválható.  Vagyis a függvény minimumát könnyen kizámíthatjuk. Első lépésben deriválunk Thétára:

$$   \frac{d}{d\theta} \mathbb E[(x-\theta)^2] =\mathbb E[-2x+2\theta] = -2\cdot \mathbb E[x]+2\cdot\theta $$

Majd megnézzük, ez hol veszi fel a minimumát, a nullát:

$$ -2\cdot \mathbb E[x]+2\cdot\theta = 0 $$

$$ \mathbb E[x] = \theta $${#eq:6}

Vagyis az átlagban éri el a minimumát a Négyzetes hiba függvény. Megfordítva a logikát: a Négyzetes hiba az *átlag becslésére* használható. 

Most nézzük a konfidencia intervallumut a becslésre. Mi lesz a  *J* és a *K* értéke?  A *J*:

$$ J(\theta ^*) = \mathbb E\left[ \frac{\partial ^2}{\partial \theta^* \partial \theta^* }  (x-\theta)^2 \right] $$

$$ J(\theta ^*) = \mathbb E[2]  = 2 $${#eq:6}

A *K* pedig:

$$ K(\theta ^*) = \text {Var}\left[ \frac{\partial }{\partial \theta^* } (x-\theta)^{2} \right] $$

$$ K(\theta ^*) =  \text {Var}\left[  -2\cdot x+2\cdot\theta  \right] $$

A variancia szabályai alapján:

$$ K(\theta ^*) = 4\cdot\text {Var}\left[ x \right] +  4\cdot\text {Var}\left[ \theta \right] $$

A $$\theta$$ egy konstans, így a varianciája 0, szóval dobhatjuk:

$$ K(\theta ^*) = 4\cdot\text {Var}\left[ x \right] $${#eq:7}

Helyettesítsünk vissza:

$$\theta^* \in \left[ \widehat{\theta} - q_{\alpha} \cdot\frac{\sqrt{ 2^{-2} \cdot  4\cdot\text {Var}\left[ x \right] } }{\sqrt{n}}, \widehat{\theta} + q_{\alpha} \cdot\frac{\sqrt{ 2^{-2} \cdot  4\cdot\text {Var}\left[ x \right] } }{\sqrt{n}} \right] $$

$$\theta^* \in \left[ \widehat{\theta}- q_{\alpha} \cdot\frac{\sqrt{ \text {Var}\left[ x \right] } }{\sqrt{n}}, \widehat{\theta} + q_{\alpha} \cdot\frac{\sqrt{ \text {Var}\left[ x \right] } }{\sqrt{n}} \right] $${#eq:8}

Amit felírhatunk egy a centrálális határeloszlás tételéből jól ismert formában is:

$$\theta^* \in  \left[ \widehat{\theta} - q_{\alpha} \cdot\frac{\sqrt{\sigma˘^2 } }{\sqrt{n}}, \widehat{\theta} + q_{\alpha} \cdot\frac{\sqrt{\sigma˘^2 } }{\sqrt{n}}  \right] $$


Készen is vagyunk. Mint látható deriválható loss függvény esetén könnyed gyakorlat a legjobb becslés és a konfidencia intervallumának számítása. A következő részben megnézzük, mit teszünk ha sajnos nem tudunk deriválni. 

# Reklám
A bejegyzés az ingyenes valós idejű közös munkát támogató online [μr² Markdown szerkesztővel](https://mur2.co.uk/editor) készült. A Markdown változat letölthető [innen](https://github.com/sajozsattila/blog/tree/master/Markdown), egy szebben formázott HTML, EPUB és PDF változat pedig: [innen](https://mur2.co.uk/reader/2220)

# Irodalom

+ [Formulating quantile regression as Linear Programming problem?](https://stats.stackexchange.com/questions/384909/formulating-quantile-regression-as-linear-programming-problem) -- stats.stackexchange.com kérdés. "Jesper for President" és "Mate Uzsoki" válasza érdekes számunkra a témához.
+ Leonard A. Stefanski és Dennis D. Boos: [The Calculus of M-Estimation](https://www.tandfonline.com/doi/abs/10.1198/000313002753631330)
+ Meral Cetin és Serpil Aktas: [Confidence Intervals Based on Robust Estimators](https://pdfs.semanticscholar.org/6b05/84eaee008fda7bbbe6c93a027e89fb315d8f.pdf)
+ Ricardo Fraiman, Victor J. Yohai és Ruben H. Zamar [Optimal Robust M-Estimates of Location](https://www.jstor.org/stable/2674022)
+ Víctor J. Yohai és Ruben H. Zamar: [Robust Nonparametric Inference for the Median](https://arxiv.org/pdf/math/0503665v1.pdf)
+ Zhengyou Zhang: [M-estimators](http://www-sop.inria.fr/odyssee/software/old_robotvis/Tutorial-Estim/node24.html)

