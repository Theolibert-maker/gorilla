# Projet Kamisado

Notre IA pour le tournoi du cours de projet. Le programme se connecte au serveur du prof (`PI2CChampionshipRunner`), s'inscrit, et joue les coups quand le serveur lui demande.

## Comment ça marche

Le jeu c'est Kamisado, un plateau 8x8 où chaque case a une couleur. Chaque joueur a 8 pions colorés. La règle bizarre du jeu : la couleur de la case sur laquelle ton pion arrive force l'adversaire à jouer son pion de cette couleur au tour d'après. Il faut amener un de ses pions sur la dernière ligne de l'autre côté du plateau pour gagner.

Les pions ne peuvent avancer que tout droit ou en diagonale avant, et ils peuvent pas sauter par-dessus un autre pion.

## Lancer le programme

D'abord installer ce qu'il faut :

```
python -m pip install -r requirement.txt
python -m pip install pytest
```

Ensuite il faut aller dans `inscription.py` et changer l'IP du serveur :

```python
HOST = "192.168.1.104"
PORT = 3000
CLIENT_PORT = 2222
```

Le `HOST` c'est l'IP de la machine où tourne le serveur du prof. `CLIENT_PORT` c'est le port sur lequel notre programme écoute.

Puis on lance simplement :

```
python main.py
```

Le programme ouvre un serveur en arrière-plan pour recevoir les requêtes, envoie l'inscription, et reste actif tant qu'on le ferme pas.

## Les fichiers

- `main.py` : démarre le serveur et envoie l'inscription
- `inscription.py` : tout ce qui touche au réseau (sockets, encodage des messages, ping, etc.)
- `moves.py` : génère les coups légaux à partir d'un plateau
- `IA.py` : la partie qui choisit le coup
- `test_kamisado.py` : les tests pytest

## La stratégie

On utilise un **negamax avec alpha-beta** et un **iterative deepening** limité par le temps.

En gros, à chaque tour on a 3 secondes max pour répondre (sinon on perd une vie). Au lieu de fixer une profondeur de recherche à l'avance, on commence à profondeur 1, puis 2, puis 3, etc. À chaque fois qu'on finit une profondeur on garde le meilleur coup trouvé. Quand le temps est écoulé on coupe la recherche (avec une exception `SearchTimeout`) et on renvoie le dernier meilleur coup. Comme ça on a toujours un coup à jouer même si on s'arrête en plein milieu d'une profondeur plus profonde.

L'évaluation d'une position regarde plusieurs choses : à quel point les pions ont avancé vers la ligne adverse, est-ce qu'ils sont au centre du plateau, est-ce que la case devant est libre, et surtout est-ce qu'il y a un chemin libre (en ligne droite ou en diagonale) jusqu'à la ligne d'arrivée. Plus le pion est proche du but avec un chemin dégagé, plus le score grimpe. Le score final c'est notre score moins celui de l'adversaire.

Pour que l'alpha-beta soit efficace on trie les coups avant de les explorer (`order_moves`). On regarde d'abord les coups qui gagnent direct, puis ceux qui font le plus avancer le pion, puis on préfère les coups en ligne droite plutôt que les diagonales.

Cas un peu spécial : si le pion qu'on est obligé de jouer (à cause de la couleur) ne peut bouger nulle part, on renvoie un coup "passe" qui revient à laisser le pion sur place. Avant d'envoyer le coup au serveur on passe par `ensure_legal_move` qui vérifie qu'il est bien dans les coups légaux, ça évite de perdre une vie bêtement à cause d'un bug.

## Communication avec le serveur

Tout passe en TCP avec du JSON, comme expliqué dans le README du prof. Les messages sont précédés de leur taille en octets (4 octets, entier non signé).

Les seules requêtes qu'on traite vraiment sont :

- `ping` → on répond `pong`
- `play` → on calcule un coup et on renvoie `{"response": "move", "move": [[r1, c1], [r2, c2]]}`

Pour le reste on renvoie une réponse par défaut.

## Bibliothèques

On a essayé de rester sur la bibliothèque standard de Python autant que possible :

- `socket` pour les connexions TCP
- `struct` pour encoder la taille des messages
- `json` pour les messages eux-mêmes
- `threading` pour faire tourner le serveur local en parallèle
- `time.perf_counter` pour gérer le timer des 3 secondes

Pour les tests on utilise `pytest` et `unittest.mock` (pour simuler des sockets sans vraiment se connecter à quelque chose). Et `coverage` pour le rapport de couverture.

## Tests

```
pytest test_kamisado.py
```

Pour avoir le rapport de couverture :

```
coverage run -m pytest test_kamisado.py
coverage report
```

Les tests couvrent la génération des coups, l'évaluation, le tri, les cas de passe, et la partie réseau (encodage/décodage des paquets).

## Auteurs

- 24355
- [matricule à compléter]
