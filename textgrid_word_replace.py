#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import argparse
from pathlib import Path

def load_word_lists(wrong_words_file, correct_words_file):
    """
    Charge les listes de mots à remplacer et leurs corrections.
    
    Args:
        wrong_words_file (str): Chemin vers le fichier contenant les mots incorrects
        correct_words_file (str): Chemin vers le fichier contenant les mots corrects
    
    Returns:
        dict: Dictionnaire de correspondance {mot_incorrect: mot_correct}
    """
    try:
        # Charger les mots incorrects
        with open(wrong_words_file, 'r', encoding='utf-8') as file:
            wrong_words = [line.strip() for line in file if line.strip()]
        
        # Charger les mots corrects
        with open(correct_words_file, 'r', encoding='utf-8') as file:
            correct_words = [line.strip() for line in file if line.strip()]
        
        # Vérifier que les deux listes ont la même longueur
        if len(wrong_words) != len(correct_words):
            raise ValueError("Les fichiers de mots incorrects et corrects doivent contenir le même nombre de lignes")
        
        # Créer le dictionnaire de correspondance
        word_map = dict(zip(wrong_words, correct_words))
        
        return word_map
    
    except Exception as e:
        print(f"Erreur lors du chargement des listes de mots: {e}")
        return {}

def correct_words_in_textgrid(filepath, word_map, backup=True):
    """
    Remplace les mots incorrects par leurs corrections dans un fichier TextGrid.
    
    Args:
        filepath (str): Chemin vers le fichier TextGrid à modifier
        word_map (dict): Dictionnaire de correspondance {mot_incorrect: mot_correct}
        backup (bool): Créer une copie de sauvegarde du fichier original
    
    Returns:
        dict: Statistiques des remplacements effectués {mot: nombre_remplacements}
    """
    try:
        # Lire le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Créer une sauvegarde si demandé
        if backup:
            backup_path = filepath + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        # Initialiser le compteur de remplacements pour chaque mot
        replacements_stats = {word: 0 for word in word_map}
        
        # Effectuer le remplacement pour chaque mot dans le dictionnaire
        modified_content = content
        for wrong_word, correct_word in word_map.items():
            # Pattern pour trouver la ligne "text = "mot"" dans le TextGrid
            pattern = r'(text\s*=\s*")' + re.escape(wrong_word) + r'(")'
            replacement = r'\1' + correct_word + r'\2'
            
            # Compter le nombre d'occurrences avant le remplacement
            count = len(re.findall(pattern, modified_content))
            replacements_stats[wrong_word] = count
            
            # Effectuer le remplacement
            modified_content = re.sub(pattern, replacement, modified_content)
        
        # Écrire le contenu modifié dans le fichier seulement s'il y a eu des remplacements
        total_replacements = sum(replacements_stats.values())
        if total_replacements > 0:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print(f"Modifié: {os.path.basename(filepath)}")
            # Afficher les détails des remplacements pour ce fichier
            for word, count in replacements_stats.items():
                if count > 0:
                    print(f"  - '{word}' → '{word_map[word]}': {count} remplacements")
        
        return replacements_stats
    
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {filepath}: {e}")
        return {word: 0 for word in word_map}

def remove_parentheses_content(filepath, backup=True):
    """
    Supprime le contenu entre parenthèses dans les valeurs de "text" dans un fichier TextGrid.
    Exemple: text = "id(le)" devient text = "id"
    
    Args:
        filepath (str): Chemin vers le fichier TextGrid à modifier
        backup (bool): Créer une copie de sauvegarde du fichier original
    
    Returns:
        int: Nombre de remplacements effectués
    """
    try:
        # Lire le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Créer une sauvegarde si demandé et si elle n'existe pas déjà
        if backup and not os.path.exists(filepath + '.bak'):
            backup_path = filepath + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        # Pattern pour trouver le contenu entre parenthèses dans les valeurs de "text"
        pattern = r'(text\s*=\s*"[^"\(]*)\([^\)]*\)([^"]*")'
        
        # Compter le nombre d'occurrences avant le remplacement
        count = len(re.findall(pattern, content))
        
        # Effectuer le remplacement
        modified_content = re.sub(pattern, r'\1\2', content)
        
        # Écrire le contenu modifié dans le fichier seulement s'il y a eu des remplacements
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print(f"Modifié (suppression de parenthèses): {os.path.basename(filepath)} - {count} remplacements")
        
        return count
    
    except Exception as e:
        print(f"Erreur lors du traitement des parenthèses dans {filepath}: {e}")
        return 0

def process_directory(directory_path, wrong_words_file=None, correct_words_file=None, recursive=False, backup=True, remove_parentheses=False, replace_hyphens=False):
    """
    Traite tous les fichiers TextGrid dans un répertoire.
    
    Args:
        directory_path (str): Chemin vers le répertoire contenant les fichiers TextGrid
        wrong_words_file (str, optional): Chemin vers le fichier contenant les mots incorrects
        correct_words_file (str, optional): Chemin vers le fichier contenant les mots corrects
        recursive (bool): Traiter récursivement les sous-répertoires
        backup (bool): Créer des copies de sauvegarde des fichiers originaux
        remove_parentheses (bool): Supprimer le contenu entre parenthèses
        replace_hyphens (bool): Remplacer les tirets et underscores par des espaces
    """
    # Charger les listes de mots si les fichiers sont fournis
    word_map = {}
    if wrong_words_file and correct_words_file:
        word_map = load_word_lists(wrong_words_file, correct_words_file)
        
        if not word_map and not remove_parentheses and not replace_hyphens:
            print("Impossible de continuer sans listes de mots valides.")
            return
        
        # Afficher les correspondances
        print("Correspondances de mots à corriger:")
        for wrong_word, correct_word in word_map.items():
            print(f"  - '{wrong_word}' → '{correct_word}'")
    
    # Rechercher les fichiers TextGrid
    if recursive:
        textgrid_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.TextGrid'):
                    textgrid_files.append(os.path.join(root, file))
    else:
        textgrid_files = glob.glob(os.path.join(directory_path, "*.TextGrid"))
    
    if not textgrid_files:
        print(f"Aucun fichier TextGrid trouvé dans {directory_path}")
        return
    
    # Initialiser les compteurs
    total_files = 0
    total_replacements = 0
    total_parentheses_removed = 0
    total_hyphens_replaced = 0
    word_totals = {word: 0 for word in word_map} if word_map else {}
    
    print(f"\nTraitement de {len(textgrid_files)} fichiers TextGrid...")
    
    # Traiter chaque fichier
    for filepath in textgrid_files:
        file_modified = False
        
        # Effectuer le remplacement de mots si nécessaire
        if word_map:
            replacements_stats = correct_words_in_textgrid(filepath, word_map, backup)
            
            # Mettre à jour les compteurs
            file_total = sum(replacements_stats.values())
            if file_total > 0:
                file_modified = True
                total_replacements += file_total
                
                # Mettre à jour les totaux par mot
                for word, count in replacements_stats.items():
                    word_totals[word] += count
        
        # Supprimer le contenu entre parenthèses si demandé
        if remove_parentheses:
            parentheses_removed = remove_parentheses_content(filepath, backup)
            if parentheses_removed > 0:
                file_modified = True
                total_parentheses_removed += parentheses_removed
        
        # Remplacer les tirets et underscores par des espaces si demandé
        if replace_hyphens:
            hyphens_replaced = replace_hyphens_underscores(filepath, backup)
            if hyphens_replaced > 0:
                file_modified = True
                total_hyphens_replaced += hyphens_replaced
        
        if file_modified:
            total_files += 1
    
    # Afficher le résumé des remplacements
    print(f"\nRésumé:")
    print(f"Nombre total de fichiers traités: {len(textgrid_files)}")
    print(f"Nombre de fichiers modifiés: {total_files}")
    
    if word_map:
        print(f"Nombre total de remplacements de mots: {total_replacements}")
        if total_replacements > 0:
            print("\nDétail des remplacements par mot:")
            for word, count in word_totals.items():
                if count > 0:
                    print(f"  - '{word}' → '{word_map[word]}': {count} remplacements")
    
    if remove_parentheses:
        print(f"Nombre total de suppressions de parenthèses: {total_parentheses_removed}")
    
    if replace_hyphens:
        print(f"Nombre total de tirets/underscores remplacés: {total_hyphens_replaced}")

def replace_hyphens_underscores(filepath, backup=True):
    """
    Remplace les tirets (-) et les underscores (_) par des espaces dans les valeurs de "text"
    dans un fichier TextGrid.
    Exemple: text = "est_ce_que" devient text = "est ce que"
    
    Args:
        filepath (str): Chemin vers le fichier TextGrid à modifier
        backup (bool): Créer une copie de sauvegarde du fichier original
    
    Returns:
        int: Nombre de remplacements effectués
    """
    try:
        # Lire le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Créer une sauvegarde si demandé et si elle n'existe pas déjà
        if backup and not os.path.exists(filepath + '.bak'):
            backup_path = filepath + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        # Pattern pour trouver les tirets et underscores dans les valeurs de "text"
        pattern_hyphen = r'(text\s*=\s*"[^"]*)[_-]([^"]*")'
        
        # Compter les occurrences initiales
        occurrences = len(re.findall(r'(text\s*=\s*"[^"]*)[-_]([^"]*")', content))
        
        # Remplacer récursivement tous les tirets et underscores par des espaces
        modified_content = content
        while True:
            # Remplacer les tirets par des espaces
            temp_content = re.sub(pattern_hyphen, r'\1 \2', modified_content)
            
            # Si plus aucun changement, sortir de la boucle
            if temp_content == modified_content:
                break
            
            modified_content = temp_content
        
        # Compter le nombre réel de remplacements (différence entre avant et après)
        remaining = len(re.findall(r'(text\s*=\s*"[^"]*)[-_]([^"]*")', modified_content))
        count = occurrences - remaining
        
        # Écrire le contenu modifié dans le fichier seulement s'il y a eu des remplacements
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print(f"Modifié (tirets/underscores → espaces): {os.path.basename(filepath)} - {count} remplacements")
        
        return count
    
    except Exception as e:
        print(f"Erreur lors du remplacement des tirets/underscores dans {filepath}: {e}")
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrige les mots dans des fichiers TextGrid selon des listes de référence")
    parser.add_argument("directory", help="Chemin vers le répertoire contenant les fichiers TextGrid")
    parser.add_argument("--wrong-words", help="Chemin vers le fichier contenant les mots incorrects")
    parser.add_argument("--correct-words", help="Chemin vers le fichier contenant les mots corrects")
    parser.add_argument("-r", "--recursive", action="store_true", help="Traiter récursivement les sous-répertoires")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de copies de sauvegarde")
    parser.add_argument("--remove-parentheses", action="store_true", help="Supprimer le contenu entre parenthèses")
    parser.add_argument("--replace-hyphens", action="store_true", help="Remplacer les tirets et underscores par des espaces")
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire existe
    if not os.path.isdir(args.directory):
        print(f"Erreur: {args.directory} n'est pas un répertoire valide")
        exit(1)
    
    # Vérifier la cohérence des arguments
    if (args.wrong_words and not args.correct_words) or (not args.wrong_words and args.correct_words):
        print("Erreur: Les fichiers de mots incorrects et corrects doivent être fournis ensemble")
        exit(1)
    
    # Vérifier que les fichiers existent s'ils sont spécifiés
    if args.wrong_words and not os.path.isfile(args.wrong_words):
        print(f"Erreur: {args.wrong_words} n'est pas un fichier valide")
        exit(1)
    
    if args.correct_words and not os.path.isfile(args.correct_words):
        print(f"Erreur: {args.correct_words} n'est pas un fichier valide")
        exit(1)
    
    # Vérifier qu'au moins une action est demandée
    if not args.wrong_words and not args.remove_parentheses and not args.replace_hyphens:
        print("Erreur: Vous devez spécifier au moins une action (remplacement de mots, suppression de parenthèses, ou remplacement de tirets/underscores)")
        exit(1)
    
    process_directory(
        args.directory, 
        args.wrong_words, 
        args.correct_words, 
        args.recursive, 
        not args.no_backup,
        args.remove_parentheses,
        args.replace_hyphens
    )
