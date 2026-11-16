# GameSquare

Diário de jogos feito com Flask, SQLite, HTML, CSS e JavaScript.

## Executar

```bash
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador.

## Personalizar as capas dos jogos

Coloque suas imagens baixadas em `static/img/`. Os nomes iniciais esperados são:

- `zelda.jpg`
- `elden-ring.jpg`
- `minecraft.jpg`
- `red-dead-redemption-2.jpg`
- `hollow-knight.jpg`
- `stardew-valley.jpg`

Os caminhos podem ser alterados na lista `games` dentro de `app.py`. Consulte `static/img/LEIA-ME.txt`.

O nome de usuário padrão do perfil é `usuariolindo` e pode ser alterado na constante `USERNAME` em `static/app.js`.
