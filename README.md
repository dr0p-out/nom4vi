Nôm4VI
======

Hán Nôm Vietnamese keyboard and tool, resources

> [!WARNING]
>
> This project is still currently a work-in-progress

## What and why?

Vietnamese, like any other language in [Sinosphere](https://en.wikipedia.org/wiki/Sinosphere) had historically used Chinese-derived scripts, and many [Sino-Xenic vocabularies](https://en.wikipedia.org/wiki/Sino-Xenic_vocabularies) still exist in the language and used even to this day. This means anyone with existing Chinese knowledge or experience with Chinese characters (for example, Japanese) could transfer their knowledge and thus learn the language faster. Or the reverse, it may also be useful for learning Chinese or Japanese with Vietnamese knowledges transferred.

## Downloads

To be done

## Installation

1. Install [Python](https://www.python.org/)

2. Install [PySide6](https://pypi.org/project/PySide6/)

> [!NOTE]
>
> You may want to use your OS distribution's package manager to do this

3. Launch `app.py`

### Dictionary

Please manually download and maintain the dictionary file (`dict.csv`) you want to use in the same directory with this application.

### Native language support

Translations needs to be compiled first, this is by design of Qt and to keep the project repository clean. Make sure you have Qt development tools installed and available in your `PATH` environment variable and run:

```shell
python build_l10n.py --compile
```

## Frequently asked questions

### How to use the keyboard outside the app?

Not planned yet, since right now, Nôm is only useful for learning, it would take many effort to make a full standard keyboard but likely isn't worth it.

### Where are all the missing features?

Things that can be done by using external tools (like searching, replacing texts) probably won't be added to keep this app simple and minimal

## Development

### Updating locale files

If the program code have added a new string, run this to make it translatable:

```shell
python build_l10n.py -u
```

### Altering translations

Open and edit `.ts` files in Qt Linguist, recompile the locale when you're done

### Adding a new locale

Define your language code in `TRANSLATIONS` array in `build_l10n.py` and re-run the update, this will generate a new empty translation file for you

## Contributing

Please report bugs, leave suggestions / start discussions, and send code patches or translation changes on project's GitHub page.

## Copying

See [license file](LICENSE.txt)
