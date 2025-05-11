MFA_lyon_dataset
- Dataset Cleanup

’python textgrid_word_replacer.py path/to/folder --wrong-words wrong_words.txt --correct-words correct_words.txt’
Available options (all can be combined):
--replace-hyphens: replaces hyphens and underscores with spaces

--remove-parentheses: removes content inside parentheses

--wrong-words and --correct-words: replaces words based on provided lists

-r, --recursive: also processes subdirectories

--no-backup: does not create backup copies

- Other transformations applied automatically:
  - Converts capital letters to lowercase
  - Removes final space before a period


- Alignment:
  We use [MFAligner](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/models/index.html).
