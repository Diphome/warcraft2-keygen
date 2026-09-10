# Warcraft II keygen

Après avoir reverse la fonction permettant de valider la CLEF-CD du jeu Warcraft II, j'ai implémenté un
script python permettant de générer des CLEFS-CD valides.

En plus de cela, j'ai implémenté un deuxième script effectuant de multiples fois l'opération pour
trouver des CLEFS-CD valides et afficher des statistiques sur le temps nécessaire et le nombre
d'échecs avant la génération d'une CLEF-CD valide.

La logique commune (algorithme de validation reverse et génération aléatoire) est factorisée dans le
module `keygen_core.py`, réutilisé par les deux scripts et couvert par des tests.

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
python warcraft2-keygen.py -n 5        # générer 5 clés
python warcraft2-keygen.py -q          # n'afficher que les clés
python warcraft2-keygen.py --seed 42   # sortie reproductible
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
