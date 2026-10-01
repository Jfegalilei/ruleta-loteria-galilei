# Ruleta de la Lotería Galilei

Ruleta para sortear la **Victory Combat 100** en la lotería de Galilei. Se proyecta en 16:9: la ruleta va en el centro y los lados quedan libres para que se paren dos presentadores.

- **Ver la ruleta:** https://jfegalilei.github.io/ruleta-loteria-galilei/
- **Archivo para el evento** (un solo HTML, funciona sin internet): https://jfegalilei.github.io/ruleta-loteria-galilei/ruleta-standalone.html
  Guárdalo con clic derecho, "Guardar como", y ábrelo con doble clic en Chrome o Edge.

## Cómo se usa

| Tecla | Qué hace |
|---|---|
| Espacio o Enter | Gira la ruleta |
| E | Abre el panel: premio, sonido de victoria, participantes, empresas, lista e historial |
| G | Muestra las zonas de los presentadores (para ubicarse al montar) |
| S | Activa o silencia el sonido |
| F | Pantalla completa |
| Esc | Cierra el panel o el anuncio del ganador |

Cada computador guarda por su cuenta los ganadores y a quienes se sacaron de la ruleta (en el navegador). Antes del evento, borra el historial y usa "Devolver a los sacados" en el panel.

## Estructura

```
index.html                  La página: HTML, CSS y JavaScript. Aquí se hacen casi todos los cambios.
assets/moto.webp            Foto de la moto (fondo transparente)
assets/siderax-moto.webp    Siderax a la izquierda de la moto, con la mano sobre el asiento de atrás (debajo de la ruleta)
assets/galilei-symbol.png   Símbolo de Galilei que acompaña a "GaliLotería"
assets/fondo-siderax.webp   Fondo: planeta de origen de Siderax, oscuro y suave
assets/fondo-ganador.webp   Fondo del anuncio del ganador: bóveda de metal oscuro abierta a un valle con arcoíris y un pedestal
assets/gali-corona.webp     Gali con corona, en el anuncio del ganador
assets/icono-juegos.svg     Ícono glow del Figma para "Juegos en el mes" (flecha circular)
assets/icono-puntaje.svg    Ícono glow del Figma para "Puntaje máximo" (check)
assets/icono-tickets.svg    Ícono glow del Figma para "Tickets" (GaliTicket)
assets/victoria.mp3         Sonido de victoria "Celebración"
data/participantes.csv      Export de Gali Admin: la fuente de los participantes
data/participantes.js       Generado desde el CSV. No editar a mano.
build/build.py              Genera participantes.js y el archivo standalone
dist/                       Salidas del build (no se suben al repo)
.github/workflows/          Publica en GitHub Pages en cada push a main
```

## Hacer cambios

1. Edita `index.html` (o reemplaza la moto, el audio o el CSV).
2. Para verlo, abre `index.html` con doble clic. Para probar todo igual que en línea (audio incluido), sírvelo:
   ```bash
   python -m http.server 8000
   ```
   y abre http://localhost:8000
3. Si cambiaste el CSV, corre `python build/build.py` para regenerar `data/participantes.js`.
4. Haz commit y push a `main`. En un par de minutos queda publicado, con el standalone regenerado.

### Actualizar participantes

Reemplaza `data/participantes.csv` por el export nuevo de Gali Admin y corre `python build/build.py`. Columnas que usa: `Player id`, `Player`, `Empresa`, `Location`, `Tickets actuales`, `Games played`, `Max score`, `Year`. Si una persona aparece en varios años, cuenta una sola vez: con sus tickets más altos, y los juegos y el puntaje del año más reciente. También se puede cargar un CSV directamente desde el panel (tecla E), sin tocar el repo.

## Reglas que no se pueden romper

Aplican a cualquier cambio, lo haga una persona o una IA.

1. **Los lados quedan vacíos.** El escenario es 16:9 fijo: la columna central mide el 52% del ancho y cada lado el 24%. Nada visible del escenario (título, ruleta, moto, textos, anuncio del ganador, confeti) puede entrar en los lados. La barra de botones flotante se esconde sola y no cuenta.
2. **El sorteo se pondera por tickets.** Se sortea un ticket con `crypto.getRandomValues` (función `randInt`, sin sesgo de módulo) y gana su dueño. No usar `Math.random` para elegir al ganador. Quien tiene 0 tickets no participa.
3. **Cada casilla mide según los tickets de su dueño.** La flecha debe detenerse dentro de la casilla del ganador. Los nombres se achican para caber en su casilla y no se dibujan si no caben legibles.
4. **Nunca mostrar el total de tickets en juego.** Ni en pantalla ni en el panel.
5. **El anuncio del ganador muestra:** la moto, el nombre, la empresa, la sede (Location), los juegos en el mes, el puntaje máximo y los tickets. Cada cifra lleva su ícono glow del Galiverso: flecha circular para los juegos, check para el puntaje y GaliTicket para los tickets. No mostrar el número de sorteo ni la cantidad de participantes.
   **Composición del anuncio:** el fondo `fondo-ganador.webp` cubre todo el escenario; sus paredes y su suelo de metal son muy oscuros para no iluminar a los presentadores, y la abertura al valle coincide con la columna central. Arriba, sobre el cielo, van el texto de arriba y el nombre; la moto y Gali con corona van parados sobre el pedestal (su parte de arriba está al 58% del alto); abajo, sobre el suelo (desde el 72%), van la empresa, la sede, las cifras y los botones. Si se cambia la imagen de fondo, hay que volver a medir esas alturas.
6. **Empresas excluidas por defecto:** Auteco, La Causa y Galilei. Se activan desde el panel.
7. **Sistema visual de marca Galilei** (definido por el equipo de diseño; no volver al estilo anterior):
   - **Las casillas van solo en los azules de la marca, sin grises ni verdes** (valores exactos de los tokens de Figma): `#ABE3F8` (info-light), `#61BDDF` (info-vivid) y `#17536A` (info-dark). Oscuro y claro se alternan: la mitad de las casillas son `#17536A` y entre cada dos va `#ABE3F8` o `#61BDDF`, turnándose. El aro y los bombillos siguen en neutros. Nombres: `#0A0B0C` sobre los azules claros y `#ABE3F8` sobre el azul oscuro.
   - **La flecha va en lima `#B3F131`.** Fuera de la ruleta y la flecha, el lima solo se admite como toque mínimo en el confeti y como estado activo o de foco en el panel: no en el botón Girar, las cifras ni el anuncio del ganador.
   - **El resto de la interfaz va en neutros:** `#0A0B0C` (fondo), `#0E1012`, `#171A1E`, `#292F36`, `#3D444C`, `#8B939E`, `#C7CCD4`, `#F0F2F5` y `#FFFFFF`. No agregar otros colores.
   - **Tipografías:** Radio Canada Big para títulos, el nombre del ganador, la empresa, las cifras y el botón Girar; Space Grotesk para el texto, los overlines, los nombres en la ruleta y el texto de abajo. Solo pesos 400 a 700.
   - **Mayúsculas solo en los overlines** (como "GaliLotería" o las etiquetas del panel), con espaciado de letras. Todo lo demás en tipo oración: "Girar", "Victory Combat 100", el nombre del ganador.
   - **El símbolo de Galilei** va junto a "GaliLotería", arriba del título.
   - **Siderax con la moto, siempre a la vista:** debajo de la ruleta va la imagen compuesta de Siderax parado a la izquierda de la moto, con la mano apoyada por encima del asiento de atrás. La moto queda centrada bajo la ruleta y su espejo termina justo debajo del botón Girar (el botón debe quedar libre). Debajo de la ruleta no va texto: la escena ocupa ese espacio. La moto debe verse igual a la foto real del producto. La ruleta mide el 70% del alto del escenario. En el anuncio del ganador va la moto sola, junto a Gali con corona.
   - **Estilo 3D del Galiverso**, como los íconos 3D y el personaje Gali del Figma "Galiverso · Galilei Learning": volumen, brillo suave y sombras coherentes con una sola luz fija arriba a la izquierda. La luz no gira con la ruleta: el aro metálico satinado, el sombreado y el reflejo son capas fijas, y solo giran las casillas y los bombillos. Las casillas conservan sus colores de marca debajo de ese sombreado.
   - **Gali solo aparece en el anuncio del ganador**, con corona junto a la moto. No va al lado de la ruleta. Su imagen sale del Figma Galiverso (sección Evergreen Stickers), solo el personaje, sin los textos tipo sticker.
   - **Fondo del planeta de Siderax** (`assets/fondo-siderax.webp`, generado a partir de la imagen de referencia): oscuro, suave y de poco contraste para no distraer de la ruleta. Los lados se atenúan con un degradado para no iluminar a los presentadores; es lo único que se permite en los lados, y debe seguir siendo tenue.
8. **Sin emojis** en la interfaz. Íconos en SVG.
9. **Todo debe funcionar sin internet en el standalone.** No cargar nada de otros sitios, salvo las fuentes de Google, que el build embebe.
10. **Si cambias un valor por defecto** (empresas excluidas, sonido elegido, etc.), sube la versión de la clave de `localStorage` (`ruleta6:` → `ruleta7:`) para que se aplique en los computadores donde ya se abrió. Eso borra su historial: avisa antes si ya se hicieron sorteos reales.
11. **Después de cambiar algo, prueba un giro completo:** que el ganador anunciado sea el mismo nombre que marca la flecha, y que los lados sigan vacíos (tecla G).
