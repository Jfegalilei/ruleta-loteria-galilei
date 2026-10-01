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
assets/galilei-symbol.png   Símbolo de Galilei, arriba a la derecha de la pantalla
assets/gali-dinero.webp      Gali con la bolsa de dinero (anuncio de Auteco y Reviews), imagen del equipo recortada
assets/siderax-dinero.webp   Siderax con la bolsa de dinero (debajo de la ruleta en Auteco y Reviews), imagen del equipo con ajuste suave a la luz nocturna, más en la bolsa (build/integrar-escena.py, fuerza 0.25 y cálidos 0.6)
assets/fondo-siderax.webp   Fondo: planeta de origen de Siderax, oscuro y suave
assets/fondo-ganador.webp   Fondo del anuncio del ganador: bóveda de metal oscuro abierta a un valle con arcoíris y un pedestal
assets/cuarto.webp          Transición: cuarto con la puerta abierta al planeta de Siderax, sin pedestal
assets/transicion.mp4       Transición: la cámara retrocede por el planeta hasta el cuarto (recortado 4% para calzar con cuarto.webp)
assets/puerta-cerrada.webp  Transición: la misma puerta cerrada (se usan sus dos hojas)
assets/laurel.svg          Rama de laurel dorada para el título del anuncio
assets/moto-gali.webp       Moto con Gali (gafas) apoyado en la rueda delantera, en el anuncio del ganador
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

## Datos siempre del repo

- Al abrir el link, la lista se pide como `data/participantes.js?t=<hora>`: nunca se usa una copia guardada (ni del navegador ni de GitHub Pages), así que se ven los datos que estén en el repo en ese momento.
- La página siempre arranca con los datos del repo: participantes, empresas excluidas de base, premio y sin foto. Lo que alguien cambie o cargue desde el panel vale mientras la página esté abierta y solo en ese navegador; al volver a abrirla se recargan los del repo. Se recuerdan entre visitas solo los sacados, el historial y el sonido.

## Sumar tickets durante la transmisión (hoja de Google)

La hoja de Google de la moto ("GaliLotería Septiembre 2026") tiene un script (Extensiones > Apps Script) que al abrirla agrega tres columnas sin tocar las demás: `sumar_10` (casillas que funcionan como interruptor: marcada suma 10 tickets a esa persona y se queda marcada; desmarcada vuelve a 0), `tickets_sumados` (fórmula: 10 si está marcada, 0 si no) y `tickets_totales` (fórmula), con filtros en todas las columnas para ordenar. Antes del sorteo se descarga la hoja (.xlsx o .csv) y se convierte con el mismo script de abajo, que suma `tickets_sumados` a `tickets_actuales`.

En pantalla la lotería de reviews se llama "Reseñas" (selector, cifra del anuncio y textos del panel); internamente su id sigue siendo `reviews` (`?loteria=reviews`).

## Sumar tickets durante la transmisión (en Excel)

Quien maneja la ruleta no suma tickets desde la página. Se hace en el Excel de la lotería con dos columnas extra: `tickets_a_sumar` (amarilla, se escribe cuántos sumar; negativo resta) y `tickets_totales` (verde, fórmula). Antes del sorteo se convierte y se publica:

```
python build/excel-a-csv.py "GaliLotería Septiembre 2026 (para sumar tickets).xlsx" data/participantes.csv
python build/build.py
```

El script pone en `tickets_actuales` el total (lo calcula él mismo, no depende de la fórmula) y quita las columnas de apoyo. Después del push, quienes manejan la ruleta solo refrescan la página: la lista se carga sin caché.

## Varias loterías

El selector "Lotería activa" (panel, tecla E) cambia entre las loterías de `data/loterias.json`. También se puede abrir una directamente con `?loteria=<id>` (por ejemplo `?loteria=auteco`). Hoy hay tres:

| id | Lotería | CSV | Imágenes |
| --- | --- | --- | --- |
| `moto` | Moto Victory Combat 100 | `data/participantes.csv` | Siderax con la moto y moto con Gali |
| `auteco` | Auteco ($5.000.000 Pesos) | `data/loteria-auteco.csv` | Siderax con el dinero debajo de la ruleta (`siderax-dinero.webp`) y Gali con el dinero en el anuncio (`gali-dinero.webp`) |
| `reviews` | Reseñas ($500.000 Pesos) | `data/loteria-reviews.csv` | Siderax con el dinero debajo de la ruleta (`siderax-dinero.webp`) y Gali con el dinero en el anuncio (`gali-dinero.webp`) |

**Reviews es distinta:** no cuenta tickets, juegos ni puntaje. Cada review es una oportunidad (columna `Reviews`, o las que diga `columnas` en `loterias.json`), y solo participan quienes tienen 50 o más (`minimo`). Su CSV (export "Reviews Ambassadors": `Nombre`, `location_name`, `company`, `reviews`) trae una fila por persona y sede y no tiene Player id: se identifica a cada persona por nombre + empresa y se suman sus reviews de todas las sedes (`sumar` en `loterias.json`; el panel hace lo mismo al cargar el CSV); la sede que se muestra es la de más reviews. En el anuncio sale una sola cifra, las reviews, con `assets/icono-reviews.svg` (la estrella amarilla de las reseñas de Google, #FBBC04, plana); al girar siguen volando GaliTickets.

- Cada lotería tiene sus propios participantes, título del premio, imágenes, empresas excluidas, sacados e historial. Cambiar de lotería recarga la página y no toca las demás.
- Datos de septiembre 2026 (llegaron en Excel y se pasaron a CSV con los enteros sin ".0"): la de la moto (GaliLotería) llegó después como CSV con columnas `jugador`, `games_played`, `max_score`, `empresa`, `sede`, `tickets_actuales` y sin Player id (cada persona se identifica por nombre + empresa); los nombres de columna se reconocen sin importar mayúsculas, tildes ni guiones bajos; la de Auteco no trae empresa (`"empresa": "Auteco"` en `loterias.json`); la sede es su `Location` (el punto de venta) y, si faltara, se usa la columna `Rol` y sus columnas son `Juegos sept` y `Puntaje max sept`.
- La de la moto debe seguir siendo la primera y con id `moto`: usa las claves de `localStorage` de siempre (`ruleta6:...`); las demás usan `ruleta6:<id>:...`.
- Para agregar o cambiar una: edita `data/loterias.json` (`id`, `nombre` del selector, `titulo` del premio, `csv` y, salvo la moto, `escena` = imagen debajo de la ruleta y `premio` = imagen sobre el pedestal del anuncio, o `null` para ninguna; opcionales `excluidas` (la de Auteco excluye solo La Causa y Galilei; la de Reviews, solo Auteco y Galilei: La Causa participa), `unidad`, `minimo` y `columnas`), pon el CSV en `data/` y corre `python build/build.py`. Las imágenes se embeben en el standalone.
- Para verificar el sorteo de una lotería: `node build/verificar-sorteo.js 3000000 auteco`.

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

1. **Los lados quedan vacíos.** El escenario es 16:9 fijo: la columna central mide el 52% del ancho y cada lado el 24%. Nada visible del escenario (título, ruleta, moto, textos, anuncio del ganador, confeti) puede entrar en los lados. Sobre todas las escenas hay una capa (`.stage::after`) que oscurece los bordes laterales (74% de negro en el borde); no la quites. Excepciones: el símbolo de Galilei en la esquina de arriba a la derecha (por encima de la cabeza de los presentadores) y los tickets que salen volando de la ruleta mientras gira, que cruzan los lados de paso hasta salir de la pantalla. La barra de botones flotante se esconde sola y no cuenta.
2. **El giro dura entre 10 y 15 segundos** (al azar, con `randInt`). **El sorteo se pondera por tickets.** Se sortea un ticket con `crypto.getRandomValues` (función `randInt`, sin sesgo de módulo) y gana su dueño. No usar `Math.random` para elegir al ganador. Quien tiene 0 tickets no participa. Se anuncia a la persona sorteada (no a la que "parece" marcar la flecha) y se comprueba que la flecha haya quedado en su casilla; el punto donde cae dentro de la casilla también sale de `randInt`. Si la lista del repo cambia (`data/participantes.js`), los computadores que ya la habían abierto la recargan solos (firma `dataSig`), para no sortear con una lista vieja guardada en el navegador. Para comprobarlo: `node build/verificar-sorteo.js` usa las funciones reales de `index.html` y los datos reales, simula 3 millones de sorteos y verifica que la flecha siempre caiga en la casilla del sorteado y que cada persona gane en proporción a sus tickets (chi-cuadrado al 99,9%).
3. **Cada casilla mide según los tickets de su dueño.** La flecha debe detenerse dentro de la casilla del ganador. Los nombres se achican para caber en su casilla y no se dibujan si no caben legibles.
4. **Nunca mostrar el total de tickets en juego.** Ni en pantalla ni en el panel.
5. **Transición al ganador** (unos 12 segundos, después de que la flecha celebra): se van el título y la marca; la ruleta con Siderax y la moto se queda parada en el planeta mientras entra debajo el video `transicion.mp4` (8 s, con su propio sonido, que se apaga suave en su último segundo y medio para no cortarse en seco), donde la cámara retrocede por el planeta y sale por la puerta del cuarto: la escena (`.scene.viaje`, z 5, sin fondo) sigue cuadro por cuadro la posición y la escala del punto del suelo donde pisan Siderax y la moto (49,4% / 96,9%), rastreadas en el video con flujo óptico (`TRAYECTO` en index.html; si cambia el video hay que volver a rastrearla con `python build/rastrear-transicion.py`, que necesita `opencv-python-headless`, y pegar el resultado de `build/rastreo/track.json`), así que no se despega del suelo; a los 5,3 s del video le cae un rayo (`rayo()`: dos golpes con parpadeo, destello de toda la pantalla y trueno) y en el segundo golpe desaparece junto con la ruleta, para no verla achicarse; al terminar queda quieto `cuarto.webp` (el video está recortado para que su último cuadro calce con él), las dos hojas de `puerta-cerrada.webp` se cierran en 2,05 s al ritmo de `assets/puerta-cierre.mp3` (sonido del equipo: mecanismo y golpe al final, con sacudida de pantalla), quedan cerradas unos 2,4 s mientras se cuela un brillo dorado intenso por la rendija del medio (`.rendija`) y por debajo de las hojas con su reflejo en el piso (`.rendija-piso`); solo con la puerta cerrada, se apaga al empezar a abrirse y se abren mostrando el anuncio, con la moto ya en el pedestal; en la lotería de la moto, al abrirse suena `assets/moto-arranque.mp3` (la moto arrancando, subida 14 dB con limitador para que se oiga fuerte). Las hojas cubren la abertura del 19,9% al 77,6% del ancho (la izquierda empieza antes para tapar el borde de la abertura del fondo del ganador) y del 15,5% al 88,5% del alto, unidas al 49,7%. Si se cambia el video, hay que volver a alinear su último cuadro con el cuarto. Con movimiento reducido activado, el anuncio aparece directo.
6. **El anuncio del ganador muestra:** la moto, el nombre, la empresa, la sede (Location), los juegos en el mes, el puntaje máximo y los tickets. Cada cifra lleva su ícono glow del Galiverso: flecha circular para los juegos, check para el puntaje y GaliTicket para los tickets. No mostrar el número de sorteo ni la cantidad de participantes.
   **Composición del anuncio:** el fondo `fondo-ganador.webp` cubre todo el escenario; sus paredes y su suelo de metal son muy oscuros para no iluminar a los presentadores, y la abertura al valle coincide con la columna central. Arriba va el título entre dos laureles dorados (`laurel.svg`, el derecho reflejado): el nombre (lo más grande del anuncio, en el dorado degradado de los laureles) y la empresa · sede; la moto con Gali apoyado (`moto-gali.webp`) va sobre el pedestal, y el nombre del premio va en letras de luz cálida sobre el frente del pedestal (SVG `#wPlaca`: centro casi blanco, degradado a ámbar y resplandor ámbar; se achica si el nombre no cabe), debajo de la moto (`.w-placa`, franja libre del 71,2% al 77,9% del alto; ya se ve al abrirse las puertas). Arriba no va "Ganador/a del mes" ni el premio, solo el nombre y la empresa · sede. La moto va centrada en la pantalla y Gali a su derecha (su parte de arriba está al 67,5% del alto); abajo van las cifras y los botones, con el frente del pedestal detrás. La imagen la hizo el equipo (reescalada a 4K): abertura del 21% al 77% del ancho, desde el 18% del alto (debajo del marco del portón), con paisaje dorado y suave, dentro de la columna central: las zonas de los presentadores son pared de metal oscuro. Si se cambia la imagen de fondo, hay que volver a medir esas alturas.
7. **Empresas excluidas por defecto:** Auteco, La Causa y Galilei. Se activan desde el panel.
8. **Sistema visual de marca Galilei** (definido por el equipo de diseño; no volver al estilo anterior):
   - **Las casillas van solo en los azules de la marca, sin grises ni verdes** (valores exactos de los tokens de Figma): `#ABE3F8` (info-light), `#61BDDF` (info-vivid) y `#17536A` (info-dark). Oscuro y claro se alternan: la mitad de las casillas son `#17536A` y entre cada dos va `#ABE3F8` o `#61BDDF`, turnándose. El aro y los bombillos siguen en neutros. Nombres: `#0A0B0C` sobre los azules claros y `#ABE3F8` sobre el azul oscuro.
   - **La flecha va en lima `#B3F131`.** Fuera de la ruleta y la flecha, el lima solo se admite en el confeti y como estado activo o de foco en el panel: no en el botón Girar, las cifras ni el anuncio del ganador.
   - **El resto de la interfaz va en neutros:** `#0A0B0C` (fondo), `#0E1012`, `#171A1E`, `#292F36`, `#3D444C`, `#8B939E`, `#C7CCD4`, `#F0F2F5` y `#FFFFFF`. No agregar otros colores.
   - **Tickets en movimiento.** Mientras la ruleta gira, salen GaliTickets (`icono-tickets.svg`) despedidos del borde en la dirección del giro: muchos a toda velocidad y cada vez menos al frenar. Se dibujan en un canvas de todo el escenario, detrás del título y de Siderax con la moto, y salen de la pantalla sin cortarse en el borde de la columna. En la celebración, el confeti es una lluvia de tickets (rectángulo con muescas y línea punteada) de varios colores de la paleta de Galilei, que caen girando dentro de la columna central: primero una lluvia fuerte y después unos 3 por segundo hasta cerrar el anuncio; ninguno se corta en los bordes de la columna. La moto con Gali ya está en el pedestal cuando se abren las puertas. Junto al pedestal del anuncio hay dos volcanes de pólvora (conos en el piso, al 25,6% y 74,4% del ancho) que lanzan chispas doradas unos 14 s y, apagados, siguen a la vista hasta cerrar el anuncio. Van detrás de todos los elementos del anuncio (cifras, moto, textos), solo encima del fondo. Con movimiento reducido no aparecen ni los tickets ni las chispas.
   - **Tipografías:** Radio Canada Big para títulos, el nombre del ganador, la empresa, las cifras y el botón Girar; Space Grotesk para el texto, los overlines, los nombres en la ruleta y el texto de abajo. Solo pesos 400 a 700.
   - **Mayúsculas solo en las etiquetas del panel**, con espaciado de letras. Todo lo demás en tipo oración: "Girar", "Victory Combat 100", el nombre del ganador.
   - **El símbolo de Galilei** va solo (sin el texto "GaliLotería", que se quitó a pedido del usuario), arriba a la derecha de la pantalla y centrado a la altura del título, encima de la capa que oscurece los bordes; se oculta con la ruleta durante la transición y el anuncio.
   - **Siderax con la moto, siempre a la vista:** debajo de la ruleta va la imagen compuesta de Siderax parado a la izquierda de la moto, con la mano apoyada por encima del asiento de atrás. La moto queda centrada bajo la ruleta y su espejo termina justo debajo del botón Girar (el botón debe quedar libre). Debajo de la ruleta no va texto: la escena ocupa ese espacio. La moto debe verse igual a la foto real del producto. La ruleta mide el 70% del alto del escenario. En el anuncio del ganador va la moto con Gali apoyado en la rueda delantera.
   - **Estilo 3D del Galiverso**, como los íconos 3D y el personaje Gali del Figma "Galiverso · Galilei Learning": volumen, brillo suave y sombras coherentes con una sola luz fija arriba a la izquierda. La luz no gira con la ruleta: el aro metálico satinado, el sombreado y el reflejo son capas fijas, y solo giran las casillas y los bombillos. Las casillas conservan sus colores de marca debajo de ese sombreado.
   - **Gali solo aparece en el anuncio del ganador**, con gafas, apoyado en la rueda delantera de la moto (`moto-gali.webp`, imagen hecha por el equipo). No va al lado de la ruleta.
   - **Fondo del planeta de Siderax** (`assets/fondo-siderax.webp`, generado a partir de la imagen de referencia): oscuro, suave y de poco contraste para no distraer de la ruleta. Los lados se atenúan con un degradado para no iluminar a los presentadores; es lo único que se permite en los lados, y debe seguir siendo tenue.
9. **Sin emojis** en la interfaz. Íconos en SVG.
10. **Todo debe funcionar sin internet en el standalone.** No cargar nada de otros sitios, salvo las fuentes de Google, que el build embebe.
11. **Si cambias un valor por defecto** (empresas excluidas, sonido elegido, etc.), sube la versión de la clave de `localStorage` (`ruleta6:` → `ruleta7:`) para que se aplique en los computadores donde ya se abrió. Eso borra su historial: avisa antes si ya se hicieron sorteos reales.
12. **Después de cambiar algo, prueba un giro completo:** que el ganador anunciado sea el mismo nombre que marca la flecha, y que los lados sigan vacíos (tecla G).
