#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import argparse
from pathlib import Path

def debug_text_field(content):
    """
    Fonction de débogage pour extraire et afficher tous les champs text du contenu
    """
    pattern = r'text\s*=\s*"([^"]*)"'
    matches = re.findall(pattern, content)
    print("Champs text trouvés:")
    for i, match in enumerate(matches):
        print(f"{i+1}. '{match}'")
    return matches

def fix_space_before_dot(filepath, backup=True, debug=False):
    """
    Traite spécifiquement le cas où un espace est suivi par un point collé
    (ex: "arbre. " → "arbre . ")
    
    Args:
        filepath (str): Chemin vers le fichier TextGrid à modifier
        backup (bool): Créer une copie de sauvegarde du fichier original
        debug (bool): Activer le mode débogage pour afficher plus d'informations
    
    Returns:
        int: Nombre de remplacements effectués
    """
    try:
        # Lire le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if debug:
            print(f"Analyse du fichier: {filepath}")
            text_fields = debug_text_field(content)
        
        # Créer une sauvegarde si demandé et si elle n'existe pas déjà
        if backup and not os.path.exists(filepath + '.bak'):
            backup_path = filepath + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        # Pattern pour trouver les cas où le mot est suivi d'un point puis immédiatement du guillemet fermant
        pattern1 = r'(text\s*=\s*".*\w)(\.)(")'
        
        # Pattern pour trouver les cas spécifiques comme "arbre. " (mot suivi d'un point puis d'un espace)
        pattern2 = r'(text\s*=\s*".*\w)(\.)\s+(")'
        
        # Fonction de remplacement pour ajouter un espace avant le point (cas 1)
        def add_space_before_dot1(match):
            return match.group(1) + " ." + match.group(3)
        
        # Fonction de remplacement pour ajouter un espace avant le point (cas 2)
        def add_space_before_dot2(match):
            return match.group(1) + " ." + match.group(3)
        
        # Compter les occurrences de chaque pattern
        count1 = len(re.findall(pattern1, content))
        count2 = len(re.findall(pattern2, content))
        
        if debug:
            print(f"Pattern 1 (mot.): {count1} occurrences")
            print(f"Pattern 2 (mot .): {count2} occurrences")
        
        # Effectuer les remplacements
        modified_content = re.sub(pattern1, add_space_before_dot1, content)
        modified_content = re.sub(pattern2, add_space_before_dot2, modified_content)
        
        # Total des modifications
        total_count = count1 + count2
        
        # Vérifier si des changements ont été effectués
        if modified_content != content:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            details = []
            if count1 > 0:
                details.append(f"{count1} points collés corrigés")
            if count2 > 0:
                details.append(f"{count2} points avec espace unique corrigés")
            
            details_str = ", ".join(details)
            print(f"Modifié: {os.path.basename(filepath)} - {total_count} remplacements ({details_str})")
            
            if debug:
                print("Après modification:")
                debug_text_field(modified_content)
        elif debug:
            print(f"Aucun changement nécessaire dans {os.path.basename(filepath)}")
        
        return total_count
    
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {filepath}: {e}")
        return 0

def process_directory(directory_path, recursive=False, backup=True, debug=False):
    """
    Traite tous les fichiers TextGrid dans un répertoire.
    
    Args:
        directory_path (str): Chemin vers le répertoire contenant les fichiers TextGrid
        recursive (bool): Traiter récursivement les sous-répertoires
        backup (bool): Créer des copies de sauvegarde des fichiers originaux
        debug (bool): Activer le mode débogage
    """
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
    
    print(f"\nTraitement de {len(textgrid_files)} fichiers TextGrid...")
    
    # Traiter chaque fichier
    for filepath in textgrid_files:
        replacements = fix_space_before_dot(filepath, backup, debug)
        
        if replacements > 0:
            total_files += 1
            total_replacements += replacements
    
    # Afficher le résumé des remplacements
    print(f"\nRésumé:")
    print(f"Nombre total de fichiers traités: {len(textgrid_files)}")
    print(f"Nombre de fichiers modifiés: {total_files}")
    print(f"Nombre total de corrections d'espacement avant/après le point: {total_replacements}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrige l'espacement autour des points dans les fichiers TextGrid")
    parser.add_argument("directory", help="Chemin vers le répertoire contenant les fichiers TextGrid")
    parser.add_argument("-r", "--recursive", action="store_true", help="Traiter récursivement les sous-répertoires")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de copies de sauvegarde")
    parser.add_argument("--debug", action="store_true", help="Activer le mode débogage")
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire existe
    if not os.path.isdir(args.directory):
        print(f"Erreur: {args.directory} n'est pas un répertoire valide")
        exit(1)
    
    process_directory(
        args.directory, 
        args.recursive, 
        not args.no_backup,
        args.debug
    )
