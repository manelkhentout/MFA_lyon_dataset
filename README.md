# MFA\_lyon\_dataset

## Dataset Cleanup

To clean the dataset, run:

```bash
python textgrid_word_replacer.py path/to/folder --wrong-words wrong_words.txt --correct-words correct_words.txt
```

### Available Options (combinable):

* `--replace-hyphens`: Replace hyphens and underscores with spaces
* `--remove-parentheses`: Remove content within parentheses
* `--wrong-words` / `--correct-words`: Replace words based on the provided lists
* `-r`, `--recursive`: Also process subdirectories
* `--no-backup`: Do not create backup copies

### Automatic Transformations:

* Convert capital letters to lowercase.
* Remove final space before a word.

## Alignment

We use **MFAligner** for alignment.


