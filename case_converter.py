#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import argparse
from pathlib import Path

def convert_case_in_textgrid(filepath, to_lowercase=True, backup=True):
    """
    Convertit les valeurs des champs "text" de majuscules en minuscules (ou inversement)
    dans un fichier TextGrid.
    
    Args:
        filepath (str): Chemin vers le fichier TextGrid à modifier
        to_lowercase (bool): True pour convertir en minuscules, False pour convertir en majuscules
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
        
        # Pattern pour trouver les valeurs des champs "text"
        pattern = r'(text\s*=\s*")([^"]*?)(")'
        
        # Fonction pour le remplacement
        def case_replace(match):
            before = match.group(1)
            text = match.group(2)
            after = match.group(3)
            
            # Convertir le texte en minuscules ou majuscules selon le paramètre
            if to_lowercase:
                new_text = text.lower()
            else:
                new_text = text.upper()
            
            # Ne retourner le remplacement que si le texte a changé
            if new_text != text:
                return before + new_text + after
            else:
                return match.group(0)
        
        # Compter le nombre d'occurrences avant le remplacement qui seraient modifiées
        count = 0
        for match in re.finditer(pattern, content):
            text = match.group(2)
            new_text = text.lower() if to_lowercase else text.upper()
            if new_text != text:
                count += 1
        
        # Effectuer le remplacement
        modified_content = re.sub(pattern, case_replace, content)
        
        # Écrire le contenu modifié dans le fichier seulement s'il y a eu des remplacements
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            conversion_type = "majuscules → minuscules" if to_lowercase else "minuscules → majuscules"
            print(f"Modifié ({conversion_type}): {os.path.basename(filepath)} - {count} remplacements")
        
        return count
    
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {filepath}: {e}")
        return 0

def process_directory(directory_path, to_lowercase=True, recursive=False, backup=True):
    """
    Traite tous les fichiers TextGrid dans un répertoire.
    
    Args:
        directory_path (str): Chemin vers le répertoire contenant les fichiers TextGrid
        to_lowercase (bool): True pour convertir en minuscules, False pour convertir en majuscules
        recursive (bool): Traiter récursivement les sous-répertoires
        backup (bool): Créer des copies de sauvegarde des fichiers originaux
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
    
    conversion_type = "majuscules → minuscules" if to_lowercase else "minuscules → majuscules"
    print(f"\nTraitement de {len(textgrid_files)} fichiers TextGrid pour conversion {conversion_type}...")
    
    # Traiter chaque fichier
    for filepath in textgrid_files:
        replacements = convert_case_in_textgrid(filepath, to_lowercase, backup)
        
        if replacements > 0:
            total_files += 1
            total_replacements += replacements
    
    # Afficher le résumé des remplacements
    print(f"\nRésumé:")
    print(f"Nombre total de fichiers traités: {len(textgrid_files)}")
    print(f"Nombre de fichiers modifiés: {total_files}")
    print(f"Nombre total de remplacements {conversion_type}: {total_replacements}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertit la casse des valeurs 'text' dans les fichiers TextGrid")
    parser.add_argument("directory", help="Chemin vers le répertoire contenant les fichiers TextGrid")
    parser.add_argument("--to-uppercase", action="store_true", help="Convertir en majuscules au lieu de minuscules")
    parser.add_argument("-r", "--recursive", action="store_true", help="Traiter récursivement les sous-répertoires")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de copies de sauvegarde")
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire existe
    if not os.path.isdir(args.directory):
        print(f"Erreur: {args.directory} n'est pas un répertoire valide")
        exit(1)
    
    process_directory(
        args.directory, 
        not args.to_uppercase,  # Par défaut, conversion en minuscules
        args.recursive, 
        not args.no_backup
    )
