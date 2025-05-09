# MFA_lyon_dataset

##Cleanup the dataset:
python textgrid_word_replacer.py chemin/vers/dossier --wrong-words mots_incorrects.txt --correct-words mots_corrects.txt
Options disponibles (toutes combinables)

--replace-hyphens : Remplace les tirets et underscores par des espaces
--remove-parentheses : Supprime le contenu entre parenthèses
--wrong-words et --correct-words : Remplace les mots selon des listes
-r, --recursive : Traite aussi les sous-répertoires
--no-backup : Ne crée pas de copies de sauvegarde
##MFA
