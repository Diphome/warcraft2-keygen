# Warcraft II keygen

Après avoir reverse la fonction permettant de valider la CLEF-CD du jeu Warcraft II, j'ai implémenté un
script python permettant de générer des CLEFS-CD valides.

En plus de cela, j'ai implémenté un deuxième script effectuant de multiples fois l'opération pour
trouver des CLEFS-CD valides et afficher des statistiques sur le temps nécessaire et le nombre
d'échecs avant la génération d'une CLEF-CD valide.

La logique commune (algorithme de validation reverse et génération) est factorisée dans le
module `keygen_core.py`, réutilisé par les deux scripts et couvert par des tests.

### Génération directe (sans brute force)

L'analyse de l'algorithme de validation montre qu'il est *séparable* :

- `principal_key_score` est un masque de 8 bits où le bit `i` vaut 1 si et seulement si la paire `i`
  de la clé produit une retenue (`b + 24·a >= 256`). Chaque bit ne dépend que de sa propre paire.
- `key_score` ne dépend que des 16 quartets de la clé dérivée.

On peut donc fixer les 7 premières paires, puis énumérer les 576 combinaisons possibles de la
dernière paire et garder la première qui équilibre les deux scores. `keygen_core.construct_valid_key`
génère ainsi une clé valide en temps quasi constant, sans brute force (utilisé par défaut ; passer
`--brute-force` pour l'ancienne recherche aléatoire).

## Installation

La génération de clés n'a besoin que de la bibliothèque standard de Python (>= 3.8).
`matplotlib` n'est requis que pour le graphique du script de statistiques :

```bash
pip install -r requirements.txt
```

## Usage

Générer une CLEF-CD valide :

```bash
python warcraft2-keygen.py
```

Options utiles :

```bash
python warcraft2-keygen.py -n 5          # générer 5 clés
python warcraft2-keygen.py -q            # n'afficher que les clés
python warcraft2-keygen.py --seed 42     # sortie reproductible
python warcraft2-keygen.py --brute-force # ancienne recherche aléatoire
```

Afficher les statistiques concernant la génération de CLEFS-CD valides :

```bash
python warcraft2-keygen-stats.py
```

Options utiles :

```bash
python warcraft2-keygen-stats.py -d 30        # tourner 30 secondes
python warcraft2-keygen-stats.py --no-plot    # sans graphique
python warcraft2-keygen-stats.py -o stats.png # enregistrer le graphique dans un fichier
```

## Tests

```bash
python test_keygen.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
