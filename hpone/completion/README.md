# HPone Bash Completion

Script bash completion untuk aplikasi HPone Docker Template Manager.

## Instalasi

```bash
# Instalasi otomatis
chmod +x hpone/completion/install.sh
./hpone/completion/install.sh

# Atau instalasi manual
source hpone/completion/hpone-completion.bash
```

## Penggunaan

```bash
./app.py <TAB>                    # Melengkapi command
./app.py inspect <TAB>            # Melengkapi nama tool
./app.py up <TAB>                 # Melengkapi tool atau --all
./app.py clean --all <TAB>        # Melengkapi opsi
```

## Uninstall

```bash
./hpone/completion/uninstall.sh
```

## File yang Tersedia

- `hpone-completion.bash` - Script bash completion
- `install.sh` - Script instalasi
- `uninstall.sh` - Script uninstall
- `README.md` - Dokumentasi ini

## Troubleshooting

Jika completion tidak bekerja:

1. Restart shell atau jalankan: `source ~/.bashrc`
2. Pastikan bash completion terinstall: `sudo apt-get install bash-completion`
3. Test manual: `source hpone/completion/hpone-completion.bash`
