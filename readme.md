QBasic Gorilla (ou Gorillas.bas) est un petit jeu vidéo créé en 1991 par Microsoft pour démontrer les capacités du langage de programmation QBasic, livré avec MS-DOS 5.0.

Dans ce jeu en 2D, deux gorilles se tiennent sur les toits d’immeubles dans une ville. Le but est de lancer des bananes explosives pour toucher le gorille adverse. Le joueur doit choisir l’angle et la vitesse du lancer, tout en tenant compte de la gravité et du vent, qui influencent la trajectoire du projectile.

Cahier des charges
Vous devez écrire un programme en utilisant les bibliothèques pygame et pygame_gui qui implémente le jeu Gorilla.

Votre programme devra:

Afficher des immeubles de hauteurs aléatoires (module random) (2 points)
Permettre d’entrer un angle et une vitesse initiale pour un projectile (2 point)
Simuler la trajectoire du projectile sous l’influence de la gravité (3 points)
Simuler l’effet du vent sur les projectiles (2 points)
Détecter les collisions entre le projectile et les immeubles / gorilles (3 points)
Répercuter les dégâts des explosions sur les immeubles (3 points)
Permettre d’enchainer plusieurs rounds et d’attribuer la victoire après 2 rounds gagnants (3 points)
Permettre aux joueurs de choisir un pseudo pour enregistrer leurs scores à la fin de la partie. Les scores seront enregistrés dans un fichier JSON (3 points)
Avoir un visuel particulièrement soigné (1 point)
Évaluation
Les projets sont à réaliser seul ou à deux pour la 8ème séance de labo. Durant cette séance, vous serez interrogés sur votre code. Le but de cette défense est d’identifier votre niveau de maîtrise de ce code. Le niveau de maîtrise est coté sur 1 et la note finale est calculée comme suitoù  est la note finale,  est la note de maîtrise du code et  est la note obtenue sur base du cahier des charges.

Pour les groupes de deux, chaque membre pourra avoir une note de maîtrise différente. De plus, chaque membre devra maîtriser l’ensemble du code.

Il est conseillé de ne pas faire appel à ChatGPT ou à un de ses concurrents.

Si un plagiat manifeste est constaté entre projets, tous les étudiants impliqués seront sanctionnés d’une note nulle.

Simulation
Nous avons déjà vu ensemble que pour animer un objet, il suffit de changer sa position d’une image à l’autre.

Ici on  est une position  en pixels et  et la vitesse  du projectile en pixels/seconde.  est le temps écoulé depuis le dernier affichage. En pygame, on obtient  par la pygame.Clock.

La gravité est une accélération. C’est-à-dire une variation de la vitesse d’une image à l’autreoù  est l’accélération de la gravité en pixels/seconde2.

Pour simuler le vent, il faut simuler les frottements de l’air. Dynamiquement, les frottements se manifestent sous forme d’une accélération opposée à la vitesse du projectile par rapport à l’air. Dans les cas simples (vitesses pas trop élevées) cette est linéairement proportionnelle à la vitesse.où  est la vitesse du mobile par rapport à l’air. Quand il n’y a pas de vent, cette vitesse est simplement égale à la vitesse du projectile. Mais en présence de vent

l’accélération totale que subit le projectile est la somme de l’accélération de la gravité et de l’accélération des frottements de l’air.

Remarque
En pygame nous avons l’habitude de dessiner sur la surface de l’écran que nous obtenons avec

screen = pygame.display.set_mode((800, 600))
où screen est de type pygame.Surface.

Dans ce projet, il pourrait vous être utile de créer d’autres surfaces pour y faire des dessins intermédiaires (les buildings par exemple).

# création d'une surface de taille (w, h)
surface = pygame.Surface((w, h))
Il est ensuite possible de dessiner sur cette surface de la même façon que l’on dessine sur le screen.

Pour dessiner une surface1 sur une surface2 on utilise la méthode blit():

surface2.blit(surface1, (x, y))
où (x, y) sera la position du coin supérieur gauche de la surface1 dans la surface2.

Sachez aussi qu’il est possible de récupérer la couleur d’un pixel d’une surface avec la méthode get_at():

color = surface.get_at((x, y))
où (x, y) sont les coordonnées du pixel. Cette méthode pourrait être utilisée pour détecter les collisions entre vos projectile et les buildings qui seraient dessinés dans la surface.

La documentation propre aux pygame.Surface se trouve sur:

https://pyga.me/docs/ref/surface.html
