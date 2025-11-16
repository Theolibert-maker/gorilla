# Projet Gorilla 2025

Ce dépôt contient le jeu Gorilla écrit avec `pygame` et `pygame_gui`. Une nouvelle partie
peut être relancée à tout moment en appuyant sur la touche **R**.

## Pousser vos modifications (`git push`)

1. Vérifiez l'état du dépôt local et ajoutez les fichiers voulus :
   ```bash
   git status
   git add <fichiers>
   git commit -m "Message descriptif"
   ```
2. Vérifiez que la bonne cible distante est configurée :
   ```bash
   git remote -v
   ```
   Si aucune cible n'est définie, ajoutez-la :
   ```bash
   git remote add origin <url-de-votre-depot>
   ```
3. Envoyez votre branche locale sur la branche distante voulue :
   ```bash
   git push origin <nom-de-branche>
   ```

En cas d'erreur d'authentification ou de divergence, assurez-vous de disposer des droits nécessaires et synchronisez-vous avec `git pull --rebase` avant de réessayer.
