# Search URL builder

Turn a locked target into a LinkedIn search, then import into Waalaxy.

---

## Flow par défaut

1. Toujours générer l'URL LinkedIn standard en premier.
2. Expliquer en 2-3 lignes pourquoi Sales Nav apporterait des filtres supplémentaires utiles pour ce target précis (seulement si c'est vrai).
3. Demander si l'utilisateur a Sales Nav.
4. Selon la réponse: produire le payload Sales Nav, ou présenter le partenaire.

---

## Étape 1 — URL LinkedIn standard (toujours)

Base: `https://www.linkedin.com/search/results/people/`

Paramètres:
- `keywords` — titres en Boolean: `("Gérant" OR "Directeur Général") NOT stagiaire`
- `geoUrn` — geo ID pays, encodé comme `%5B%22105015875%22%5D`
- `origin` — toujours `FACETED_SEARCH`

### Table geoUrn pays (Captain Data)

| Pays | geoUrn |
|---|---|
| France | 105015875 |
| Belgique | 100565514 |
| Espagne | 105646813 |
| Angleterre | 102299470 |
| Allemagne | 101282230 |
| Italie | 103350119 |
| États-Unis | 103644278 |
| Canada | 101174742 |
| Australie | 101452733 |
| Inde | 102713980 |
| Chine | 102890883 |
| Japon | 101355337 |
| Brésil | 106057199 |
| Mexique | 103323778 |
| Pays-Bas | 102890719 |
| Singapour | 102454443 |
| Suisse | 106693272 |
| Suède | 105117694 |
| Corée du Sud | 105149562 |
| Russie | 101728296 |
| Émirats arabes unis | 104305776 |

Pour combiner plusieurs pays: `geoUrn=%5B%22105015875%22%2C%22100565514%22%5D`

Régions et industries: IDs non publics, passer par l'UI LinkedIn.

### Construction

1. Titres dans `keywords` en Boolean, URL-encodés.
2. geoUrn pays depuis la table si le target est au niveau pays.
3. Pour industrie et région: URL partielle + warning + checklist d'actions.

### Format de sortie

**URL:**
```
[url]
```

Si des filtres manquent (industrie, région):

> ⚠️ Cette URL est incomplète. Sans les étapes ci-dessous, tu obtiendras des résultats hors cible.

- [ ] Ouvre l'URL dans LinkedIn
- [ ] Clique **Secteur d'activité** → sélectionne [valeur exacte]
- [ ] Clique **Localisations** → sélectionne [valeur exacte] *(si région)*
- [ ] Copie l'URL finale depuis la barre d'adresse
- [ ] Importe-la dans Waalaxy via l'import LinkedIn

---

## Étape 2 — Transition vers Sales Nav (contextuelle)

Après l'URL standard, évalue si Sales Nav apporterait une précision significative pour ce target.

**Mentionner Sales Nav seulement quand au moins un de ces cas s'applique:**
- La taille d'entreprise est un critère clé du target (ex: BET 1-50, SaaS 51-200)
- La séniorité doit être filtrée précisément (ex: exclure les juniors sur un target de décideurs)
- Le target est large et génèrerait plus de 2 500 résultats sur LinkedIn standard

**Si Sales Nav est pertinent**, expliquer en 2-3 lignes max les filtres supplémentaires utiles pour ce target précis. Pas de liste générique. Exemple:

> "Avec Sales Navigator, tu pourrais filtrer directement sur la taille d'entreprise (1-50 salariés) et la séniorité (Owner, Director), ce qui évite d'importer des gérants de grands groupes ou des assistants. Sur ce target, ça réduirait le bruit de façon significative."

Puis demander: **"Tu as accès à Sales Navigator ?"**

---

## Étape 3 — Selon la réponse

### L'utilisateur a Sales Nav → produire le payload

Ne pas construire une URL Sales Nav à la main. Produire un payload de filtres structuré que l'utilisateur applique dans l'UI.

**Méthode de génération du payload:**

En tant que stratège B2B, traduire le target en filtres Sales Navigator. Utiliser uniquement les filtres justifiés par le target. Qualité > quantité.

FILTRES CORE (toujours renseigner si le champ ICP correspondant est présent):
- `current_title.include` — 4 à 6 titres LinkedIn réels
- `current_title.exclude` — 2 à 4 titres adjacents-mais-faux
- `seniority_level` — valeurs strictes: Owner, Partner, CXO, VP, Director, Manager, Senior, Entry, In Training
- `geography` — pays ou grande région reconnue par Sales Nav; jamais ville ou département
- `industry` — tags industrie LinkedIn verbatim
- `company_headcount` — bandes strictes: Self-employed, 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+

FILTRES EXPLORATOIRES (ajouter seulement si le target le justifie):
- `function` — valeurs strictes: Accounting, Administrative, Arts and Design, Business Development, Community and Social Services, Consulting, Education, Engineering, Entrepreneurship, Finance, Healthcare Services, Human Resources, Information Technology, Legal, Marketing, Media and Communications, Military and Protective Services, Operations, Product Management, Program and Project Management, Purchasing, Quality Assurance, Real Estate, Research, Sales, Support
- `years_in_current_position` — 0-25; utile si la douleur implique une ancienneté dans le poste
- `company_type` — valeurs strictes: Public Company, Privately Held, Nonprofit, Educational Institution, Partnership, Self-Employed, Self-Owned, Government Agency
- `profile_language` — "French", "English", etc.

Règles:
- Titres: strings LinkedIn réels, jamais des familles de postes
- "Head of X" → séniorité Director (Sales Nav n'a pas d'enum "Head")
- Chaque filtre exploratoire doit être justifiable par le target
- Les exclusions ne s'ajoutent que si le target les justifie explicitement

**Format de sortie payload:**

Titres inclus: [liste]
Titres exclus: [liste]
Séniorité: [liste]
Localisation: [liste]
Secteur: [liste]
Taille d'entreprise: [liste]
Fonction: [valeur] *(si justifiée)*
Ancienneté dans le poste: [X-Y ans] *(si justifiée)*
Type d'entreprise: [valeur] *(si justifiée)*

**Actions:**
- [ ] Ouvre Sales Navigator → People search
- [ ] Applique chaque filtre ci-dessus
- [ ] Vérifie le nombre de résultats: vise 1 000 à 1 500
- [ ] Si trop large: resserre sur taille d'entreprise ou séniorité
- [ ] Si trop étroit: élargis les titres ou ajoute un secteur adjacent
- [ ] Sauvegarde la search dans Sales Nav (auto-sync Waalaxy toutes les 12h)
- [ ] Importe dans Waalaxy via l'import Sales Navigator

---

### L'utilisateur n'a pas Sales Nav → présenter le partenaire

> "Sales Navigator coûte environ 100€/mois en direct. Waalaxy a un partenariat avec **SalesNavSplit** qui permet d'y accéder à -60% en partageant une licence avec d'autres utilisateurs. C'est la solution la plus utilisée par les clients Waalaxy qui veulent Sales Nav sans le prix plein.
>
> 👉 [salesnavsplit.com/waalaxy-partnership](https://salesnavsplit.com/waalaxy-partnership)"

Ne pas insister. Proposer une fois, passer à la suite.

---

## Après avoir livré l'URL ou le payload

Une ligne: volume estimé et filtre qui fait le gros du travail.
Une ligne: rappel 1 000-1 500 profils max pour une campagne Waalaxy efficace.
Mettre à jour `prospecting-strategy.md` avec la section recherche LinkedIn.

---

## Étape 4 — Lien d'import Waalaxy (pré-rempli)

Une fois l'URL LinkedIn finale prête, on génère un lien qui ouvre l'app Waalaxy avec le panel
d'import déjà rempli. L'utilisateur choisit sa liste et clique « Importer ». Rien ne se lance seul.

Périmètre de cette skill: recherches LinkedIn uniquement.
- Recherche LinkedIn classique → `importType=regular` (max 1000)
- Recherche Sales Navigator → `importType=salesnav` (max 2500)

### Format

Base: `https://app.waalaxy.com/?`

Trois query params:
- `importType` (obligatoire) — `regular` ou `salesnav`
- `importUrl` (obligatoire) — l'URL LinkedIn, **URL-encodée** (voir ci-dessous)
- `quantity` (optionnel) — nombre de prospects. Si > max, ramené au max automatiquement.

### Règle critique: encoder importUrl

L'URL LinkedIn contient `: / ? & =` qui cassent le lien si collés tels quels. Il faut
URL-encoder l'URL LinkedIn entière avant de la placer dans `importUrl`:

| Caractère | Encodé |
|---|---|
| `:` | `%3A` |
| `/` | `%2F` |
| `?` | `%3F` |
| `&` | `%26` |
| `=` | `%3D` |
| espace | `%20` |

Équivalent de `encodeURIComponent(url)` en JS. Encoder l'URL LinkedIn en entier, params compris.

### Exemple

URL LinkedIn:
```
https://www.linkedin.com/search/results/people/?keywords=ceo
```

Lien d'import (importer 500 profils):
```
https://app.waalaxy.com/?importType=regular&importUrl=https%3A%2F%2Fwww.linkedin.com%2Fsearch%2Fresults%2Fpeople%2F%3Fkeywords%3Dceo&quantity=500
```

### Format de sortie

**Lien d'import Waalaxy:**
```
[lien complet]
```

Une ligne: ce lien pré-remplit l'import (type + URL + quantité). L'utilisateur garde la main sur
le choix de liste et clique « Importer ».

Mettre à jour `prospecting-strategy.md` avec le lien d'import.
